"""Caso de uso CU-06 (paso 3): el Representante envia la evaluacion con un enlace valido; se guarda, el enlace se usa y la Practica pasa a evaluada (ADR-005, ADR-006, ADR-007, ADR-008)."""

from collections.abc import Callable
from datetime import datetime
from uuid import uuid4

from aplicacion.configuracion.consultar_criterios_evaluacion import (
    ConsultarCriteriosEvaluacion,
)
from aplicacion.errores.enlace_no_valido import EnlaceNoValido
from aplicacion.errores.evaluacion_no_permitida import EvaluacionNoPermitida
from aplicacion.errores.evaluacion_no_valida import EvaluacionNoValida
from aplicacion.evaluacion.evaluacion_registrada import EvaluacionRegistrada
from aplicacion.evaluacion.solicitud_evaluacion import SolicitudEvaluacion
from aplicacion.puertos.bitacora import Bitacora
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas
from dominio.estado_practica import EstadoPractica
from dominio.evaluacion import Evaluacion


ROL_REPRESENTANTE = "RepresentanteEmpresa"


class RegistrarEvaluacion:
    """Registra la Evaluacion de la Empresa con todos los criterios de la ReglaPractica de la Practica."""

    def __init__(
        self,
        repositorio: RepositorioPracticas,
        bitacora: Bitacora,
        consultar_criterios: ConsultarCriteriosEvaluacion,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._repositorio = repositorio
        self._bitacora = bitacora
        self._consultar_criterios = consultar_criterios
        self._reloj = reloj

    def ejecutar(self, solicitud: SolicitudEvaluacion) -> EvaluacionRegistrada:
        """Valida las calificaciones, usa el enlace y guarda la evaluacion."""
        identidad = solicitud.identidad
        ahora = self._reloj()

        practica = self._repositorio.obtener_practica(identidad.id_practica)
        if practica is None or practica.estado != EstadoPractica.HORAS_COMPLETAS:
            raise EvaluacionNoPermitida("la práctica no está lista para evaluar")

        escalas = {
            criterio.nombre: criterio.escala
            for criterio in self._consultar_criterios.ejecutar(practica.version_regla)
        }  # criterios de la version de la Practica, ADR-008
        motivo = Evaluacion.motivo_invalidez(escalas, solicitud.calificaciones)
        if motivo:
            raise EvaluacionNoValida(motivo)  # no consume el enlace, para que el Representante corrija

        if not self._repositorio.marcar_enlace_usado(identidad.id_enlace):
            raise EnlaceNoValido("enlace usado")  # un solo uso, ADR-005

        evaluacion = Evaluacion(
            f"EV-{uuid4().hex[:8]}",
            practica.id,
            dict(solicitud.calificaciones),
            solicitud.observaciones,
            ahora.date(),
        )
        self._repositorio.guardar_evaluacion(evaluacion)

        evaluada = practica.evaluar()
        self._repositorio.guardar_practica(evaluada)

        for recurso, accion in (
            (f"enlace:{identidad.id_enlace}", "usar enlace de evaluación"),
            (f"evaluacion:{evaluacion.id}", "crear evaluación"),
            (
                f"practica:{evaluada.id}",
                "cambiar estado de horas completas a evaluada",
            ),
        ):
            self._bitacora.registrar(
                identidad.id_representante,
                ROL_REPRESENTANTE,
                recurso,
                accion,
                ahora,
            )

        return EvaluacionRegistrada(evaluacion.id, evaluada.id, evaluada.estado)
