"""Caso de uso CU-03: el Coordinador de Practicas asigna un Tutor a Practicas sin tutor respetando la carga maxima (ADR-004, ADR-006, ADR-007, ADR-008)."""

from collections.abc import Callable
from datetime import datetime

from aplicacion.asignacion.asignacion_realizada import AsignacionRealizada
from aplicacion.asignacion.resultado_practica import ResultadoPractica
from aplicacion.asignacion.solicitud_asignacion_tutor import SolicitudAsignacionTutor
from aplicacion.configuracion.consultar_regla_vigente import ConsultarReglaVigente
from aplicacion.errores.acceso_denegado import AccesoDenegado
from aplicacion.errores.correo_no_enviado import CorreoNoEnviado
from aplicacion.errores.tutor_no_encontrado import TutorNoEncontrado
from aplicacion.puertos.bitacora import Bitacora
from aplicacion.puertos.notificador import Notificador
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas
from dominio.estado_practica import EstadoPractica
from dominio.practica import Practica


ROL_COORDINADOR = "CoordinadorPracticas"


class AsignarTutor:
    """Asigna un Tutor a una o varias Practicas sin tutor, en el orden recibido."""

    def __init__(
        self,
        repositorio: RepositorioPracticas,
        bitacora: Bitacora,
        notificador: Notificador,
        consultar_regla: ConsultarReglaVigente,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._repositorio = repositorio
        self._bitacora = bitacora
        self._notificador = notificador
        self._consultar_regla = consultar_regla
        self._reloj = reloj

    def ejecutar(self, solicitud: SolicitudAsignacionTutor) -> AsignacionRealizada:
        """Ejecuta la asignacion y devuelve un resultado por Practica."""
        usuario = solicitud.usuario
        ahora = self._reloj()

        if usuario.rol != ROL_COORDINADOR:
            for id_practica in solicitud.ids_practicas:
                self._bitacora.registrar(
                    usuario.id,
                    usuario.rol,
                    f"practica:{id_practica}",
                    "asignar tutor",
                    ahora,
                )
            raise AccesoDenegado()

        tutor = self._repositorio.obtener_tutor(solicitud.id_tutor)
        if tutor is None:
            raise TutorNoEncontrado(solicitud.id_tutor)

        carga_maxima = self._consultar_regla.ejecutar().carga_maxima_tutor
        carga = self._repositorio.contar_practicas_activas_tutor(tutor.id)
        resultados: list[ResultadoPractica] = []

        for id_practica in solicitud.ids_practicas:
            practica = self._repositorio.obtener_practica(id_practica)
            if practica is None:
                resultados.append(
                    ResultadoPractica(
                        id_practica,
                        "no asignada: práctica no encontrada",
                    )
                )
                continue
            if practica.estado != EstadoPractica.SIN_TUTOR:
                resultados.append(
                    ResultadoPractica(
                        id_practica,
                        "no asignada: la práctica ya tiene tutor",
                    )
                )
                continue
            if not tutor.tiene_cupo(carga, carga_maxima):
                resultados.append(
                    ResultadoPractica(id_practica, "no asignada: tutor sin cupo")
                )
                continue

            asignada = practica.asignar_tutor(tutor.id)
            self._repositorio.guardar_practica(asignada)
            self._bitacora.registrar(
                usuario.id,
                usuario.rol,
                f"practica:{asignada.id}",
                "cambiar estado de sin tutor a en curso",
                ahora,
            )
            carga += 1
            self._notificar(tutor.correo, asignada)
            resultados.append(ResultadoPractica(id_practica, "asignada"))

        return AsignacionRealizada(tutor.id, tuple(resultados))

    def _notificar(self, correo_tutor: str, practica: Practica) -> None:
        """Notifica al Tutor y al Estudiante; si el correo falla, la asignacion no se revierte (ADR-007)."""
        destinatarios = [correo_tutor]
        estudiante = self._repositorio.obtener_estudiante(practica.id_estudiante)
        if estudiante is not None:
            destinatarios.append(estudiante.correo)

        try:
            self._notificador.enviar(
                destinatarios,
                "Asignación de tutor",
                f"El tutor {practica.id_tutor} acompaña la práctica "
                f"{practica.id} del estudiante {practica.id_estudiante}.",
            )
        except CorreoNoEnviado:
            pass  # queda pendiente de reenvio en el adaptador
