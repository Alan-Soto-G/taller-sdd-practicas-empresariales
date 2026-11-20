"""Caso de uso CU-10: el Estudiante consulta el estado de su practica, de sus horas, de la evaluacion y de su acta (Modulo Seguimiento; EAC-04, ADR-004, ADR-006)."""

from collections.abc import Callable
from datetime import datetime

from aplicacion.actas.consultar_acta_practica import ConsultarActaPractica
from aplicacion.errores.acceso_denegado import AccesoDenegado
from aplicacion.errores.practica_no_encontrada import PracticaNoEncontrada
from aplicacion.horas.resumir_horas_practica import ResumirHorasPractica
from aplicacion.puertos.bitacora import Bitacora
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas
from aplicacion.seguimiento.estado_practica_consultado import EstadoPracticaConsultado
from aplicacion.seguimiento.estado_practicas_estudiante import EstadoPracticasEstudiante
from aplicacion.seguimiento.solicitud_estado_practica import SolicitudEstadoPractica
from aplicacion.usuario_autenticado import UsuarioAutenticado
from dominio.practica import Practica

ROL_ESTUDIANTE = "Estudiante"


class ConsultarEstadoPractica:
    """Entrega al Estudiante el estado de sus practicas; solo lee, no cambia estado."""

    def __init__(
        self,
        repositorio: RepositorioPracticas,
        bitacora: Bitacora,
        resumir_horas: ResumirHorasPractica,
        consultar_acta: ConsultarActaPractica,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._repositorio = repositorio
        self._bitacora = bitacora
        self._resumir_horas = resumir_horas
        self._consultar_acta = consultar_acta
        self._reloj = reloj

    def ejecutar(self, solicitud: SolicitudEstadoPractica) -> EstadoPracticasEstudiante:
        """Devuelve el estado de todas las practicas del Estudiante o de una sola suya."""
        usuario = solicitud.usuario
        recurso = f"practica:{solicitud.id_practica}" if solicitud.id_practica else "practicas:estudiante"
        if usuario.rol != ROL_ESTUDIANTE:
            self._rechazar(usuario, recurso)

        if solicitud.id_practica is None:
            practicas = self._repositorio.listar_practicas_de_estudiante(usuario.id)
        else:
            practica = self._repositorio.obtener_practica(solicitud.id_practica)
            if practica is None:
                raise PracticaNoEncontrada(solicitud.id_practica)
            if practica.id_estudiante != usuario.id:
                self._rechazar(usuario, recurso)  # solo su titular (ADR-004, EAC-04)
            practicas = [practica]

        return EstadoPracticasEstudiante(
            usuario.id, tuple(self._consultar(practica) for practica in practicas)
        )

    def _consultar(self, practica: Practica) -> EstadoPracticaConsultado:
        """Reune horas (Modulo Horas), evaluacion y acta (Modulo Actas) de la Practica."""
        resumen = self._resumir_horas.ejecutar(practica.id, practica.version_regla)
        return EstadoPracticaConsultado(
            practica.id,
            practica.id_empresa,
            practica.id_tutor,
            practica.estado,
            resumen.horas_aprobadas,
            resumen.horas_requeridas,
            resumen.horas_pendientes,
            resumen.porcentaje,
            self._repositorio.obtener_evaluacion_de_practica(practica.id) is not None,
            self._consultar_acta.ejecutar(practica.id),
        )

    def _rechazar(self, usuario: UsuarioAutenticado, recurso: str) -> None:
        """Audita el acceso rechazado y lo niega (ADR-004, ADR-006)."""
        self._bitacora.registrar(usuario.id, usuario.rol, recurso, "consultar estado", self._reloj())
        raise AccesoDenegado()
