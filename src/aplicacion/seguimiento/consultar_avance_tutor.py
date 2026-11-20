"""Caso de uso CU-09: el Tutor consulta el avance de horas de sus practicas asignadas (Modulo Seguimiento; ADR-004, ADR-006, ADR-008)."""

from collections.abc import Callable
from datetime import datetime

from aplicacion.errores.acceso_denegado import AccesoDenegado
from aplicacion.errores.practica_no_encontrada import PracticaNoEncontrada
from aplicacion.horas.resumir_horas_practica import ResumirHorasPractica
from aplicacion.puertos.bitacora import Bitacora
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas
from aplicacion.seguimiento.avance_practica import AvancePractica
from aplicacion.seguimiento.avance_tutor import AvanceTutor
from aplicacion.seguimiento.solicitud_avance_tutor import SolicitudAvanceTutor
from aplicacion.usuario_autenticado import UsuarioAutenticado

ROL_TUTOR = "Tutor"


class ConsultarAvanceTutor:
    """Entrega el avance de las practicas del Tutor; solo lee, no cambia estado."""

    def __init__(
        self,
        repositorio: RepositorioPracticas,
        bitacora: Bitacora,
        resumir_horas: ResumirHorasPractica,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._repositorio = repositorio
        self._bitacora = bitacora
        self._resumir_horas = resumir_horas
        self._reloj = reloj

    def ejecutar(self, solicitud: SolicitudAvanceTutor) -> AvanceTutor:
        """Devuelve el avance de todas las practicas del Tutor o de una sola suya."""
        usuario = solicitud.usuario
        recurso = f"practica:{solicitud.id_practica}" if solicitud.id_practica else "practicas:tutor"
        if usuario.rol != ROL_TUTOR:
            self._rechazar(usuario, recurso)

        if solicitud.id_practica is None:
            practicas = self._repositorio.listar_practicas_de_tutor(usuario.id)
        else:
            practica = self._repositorio.obtener_practica(solicitud.id_practica)
            if practica is None:
                raise PracticaNoEncontrada(solicitud.id_practica)
            if practica.id_tutor != usuario.id:
                self._rechazar(usuario, recurso)  # solo su tutor asignado (ADR-004, EAC-04)
            practicas = [practica]

        avances = []
        for practica in practicas:
            resumen = self._resumir_horas.ejecutar(practica.id, practica.version_regla)
            avances.append(
                AvancePractica(
                    practica.id,
                    practica.id_estudiante,
                    practica.estado,
                    resumen.horas_aprobadas,
                    resumen.horas_requeridas,
                    resumen.horas_pendientes,
                    resumen.porcentaje,
                )
            )
        return AvanceTutor(usuario.id, tuple(avances))

    def _rechazar(self, usuario: UsuarioAutenticado, recurso: str) -> None:
        """Audita el acceso rechazado y lo niega (ADR-004, ADR-006)."""
        self._bitacora.registrar(usuario.id, usuario.rol, recurso, "consultar avance", self._reloj())
        raise AccesoDenegado()
