"""Caso de uso CU-07 (lado Worker de actas): consolida la practica, compone el acta, la guarda y reintenta hasta 3 veces (ADR-001, ADR-003, ADR-006, ADR-007, ADR-008)."""

from collections.abc import Callable
from datetime import datetime

from aplicacion.actas.resultado_generacion import ResultadoGeneracion
from aplicacion.actas.solicitud_acta import SolicitudActa
from aplicacion.errores.almacen_no_disponible import AlmacenNoDisponible
from aplicacion.errores.correo_no_enviado import CorreoNoEnviado
from aplicacion.puertos.almacen_actas import AlmacenActas
from aplicacion.puertos.bitacora import Bitacora
from aplicacion.puertos.notificador import Notificador
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas
from dominio.acta_final import ActaFinal
from dominio.estado_acta import EstadoActa
from dominio.intento_generacion import MAX_INTENTOS, IntentoGeneracion
from dominio.practica import Practica

USUARIO_WORKER = "worker-actas"
ROL_WORKER = "WorkerActas"


class GenerarActa:
    """Genera un acta en generacion; solo lo ejecuta el Worker de actas, nunca la API (ADR-001)."""

    def __init__(
        self,
        repositorio: RepositorioPracticas,
        bitacora: Bitacora,
        almacen: AlmacenActas,
        notificador: Notificador,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._repositorio = repositorio
        self._bitacora = bitacora
        self._almacen = almacen
        self._notificador = notificador
        self._reloj = reloj

    def ejecutar(self, solicitud: SolicitudActa) -> ResultadoGeneracion:
        """Hace un intento de generacion y dice si el acta quedo generada, se reintenta o queda con error."""
        ahora = self._reloj()
        acta = self._repositorio.obtener_acta(solicitud.id_acta)
        if acta is None or acta.estado != EstadoActa.EN_GENERACION:
            return ResultadoGeneracion(solicitud.id_acta, "omitida")
        practica = self._repositorio.obtener_practica(acta.id_practica)

        try:
            ruta = self._almacen.guardar(acta.id, self._componer(acta, practica))
        except AlmacenNoDisponible as error:
            self._repositorio.guardar_intento(
                IntentoGeneracion(acta.id, solicitud.intento, ahora, f"fallido: {error.mensaje}")
            )
            if solicitud.intento < MAX_INTENTOS:
                espera = IntentoGeneracion.espera_tras(solicitud.intento)
                return ResultadoGeneracion(acta.id, "reintentar", espera)
            self._cambiar_estado(acta.marcar_con_error(), ahora)
            return ResultadoGeneracion(acta.id, "con error")

        self._repositorio.guardar_intento(
            IntentoGeneracion(acta.id, solicitud.intento, ahora, "exitoso")
        )
        self._cambiar_estado(acta.marcar_generada(ruta), ahora)
        self._avisar(acta, practica)
        return ResultadoGeneracion(acta.id, "generada")

    def _componer(self, acta: ActaFinal, practica: Practica) -> bytes:
        """Consolida horas, evaluacion y ReglaPractica; documento simulado mientras se decide la libreria de PDF (DT-05)."""
        regla = self._repositorio.obtener_regla(practica.version_regla)
        horas = self._repositorio.sumar_horas_aprobadas(practica.id)
        evaluacion = self._repositorio.obtener_evaluacion_de_practica(practica.id)
        calificaciones = (
            ", ".join(f"{nombre}: {valor}" for nombre, valor in evaluacion.calificaciones.items())
            if evaluacion is not None
            else "sin evaluación"
        )
        lineas = [
            "%PDF-simulado",
            f"ACTA FINAL {acta.id}",
            f"Plantilla: {regla.plantilla_acta}",
            f"Práctica: {practica.id}",
            f"Estudiante: {practica.id_estudiante}",
            f"Empresa: {practica.id_empresa}",
            f"Tutor: {practica.id_tutor}",
            f"Horas aprobadas: {horas} de {regla.horas_requeridas}",
            f"Evaluación: {calificaciones}",
            f"Solicitada: {acta.fecha_solicitud:%Y-%m-%d %H:%M}",
        ]
        return "\n".join(lineas).encode("utf-8")

    def _cambiar_estado(self, acta: ActaFinal, ahora: datetime) -> None:
        """Guarda el acta y audita su paso desde en generacion (ADR-006)."""
        self._repositorio.guardar_acta(acta)
        self._bitacora.registrar(
            USUARIO_WORKER,
            ROL_WORKER,
            f"acta:{acta.id}",
            f"cambiar estado de en generación a {acta.estado}",
            ahora,
        )

    def _avisar(self, acta: ActaFinal, practica: Practica) -> None:
        """Avisa a tutor, representante y coordinador que el acta espera su aprobacion (CU-08); si falla, no revierte (ADR-007)."""
        tutor = self._repositorio.obtener_tutor(practica.id_tutor) if practica.id_tutor else None
        representante = self._repositorio.obtener_representante_de_empresa(practica.id_empresa)
        coordinador = self._repositorio.obtener_coordinador()
        destinatarios = [p.correo for p in (tutor, representante, coordinador) if p is not None]
        try:
            self._notificador.enviar(
                destinatarios,
                "Acta final por aprobar",
                f"El acta {acta.id} de la práctica {practica.id} espera su aprobación.",
            )
        except CorreoNoEnviado:
            pass  # el aviso queda pendiente de reenvio en el adaptador
