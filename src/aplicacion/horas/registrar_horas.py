"""Caso de uso CU-04: el Estudiante registra las horas de una semana de su Practica (EAC-01, EAC-04; ADR-004, ADR-006, ADR-007)."""

from collections.abc import Callable
from datetime import datetime
from uuid import uuid4

from aplicacion.errores.acceso_denegado import AccesoDenegado
from aplicacion.errores.practica_no_encontrada import PracticaNoEncontrada
from aplicacion.errores.registro_no_valido import RegistroNoValido
from aplicacion.horas.horas_reportadas import HorasReportadas
from aplicacion.horas.solicitud_registro_horas import SolicitudRegistroHoras
from aplicacion.puertos.bitacora import Bitacora
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas
from aplicacion.usuario_autenticado import UsuarioAutenticado
from dominio.estado_practica import EstadoPractica
from dominio.registro_horas import RegistroHoras


ROL_ESTUDIANTE = "Estudiante"
SEMANA_CON_REGISTRO = "la semana ya tiene un registro"


class RegistrarHoras:
    """Registra las horas semanales de un Estudiante en su Practica en curso."""

    def __init__(
        self,
        repositorio: RepositorioPracticas,
        bitacora: Bitacora,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._repositorio = repositorio
        self._bitacora = bitacora
        self._reloj = reloj

    def ejecutar(self, solicitud: SolicitudRegistroHoras) -> HorasReportadas:
        """Valida y guarda el registro como reportado."""
        usuario: UsuarioAutenticado = solicitud.usuario
        ahora = self._reloj()

        if usuario.rol != ROL_ESTUDIANTE:
            self._rechazar(usuario, solicitud.id_practica, ahora)

        practica = self._repositorio.obtener_practica(solicitud.id_practica)
        if practica is None:
            raise PracticaNoEncontrada(solicitud.id_practica)

        if practica.id_estudiante != usuario.id:
            self._rechazar(usuario, practica.id, ahora)

        if practica.estado != EstadoPractica.EN_CURSO:
            raise RegistroNoValido("la práctica no está en curso")

        motivo = RegistroHoras.motivo_invalidez(
            solicitud.semana,
            solicitud.horas,
            solicitud.actividades,
        )
        if motivo:
            raise RegistroNoValido(motivo)

        if self._repositorio.existe_registro_horas(
            practica.id,
            solicitud.semana,
        ):
            raise RegistroNoValido(SEMANA_CON_REGISTRO)

        registro = RegistroHoras.reportar(
            f"RH-{uuid4().hex[:8]}",
            practica.id,
            solicitud.semana,
            solicitud.horas,
            solicitud.actividades,
            ahora.date(),
        )
        if not self._repositorio.guardar_registro_horas(registro):
            # Otra petición simultánea ganó; 0 duplicados, EAC-01.
            raise RegistroNoValido(SEMANA_CON_REGISTRO)

        self._bitacora.registrar(
            usuario.id,
            usuario.rol,
            f"registro_horas:{registro.id}",
            "crear con estado reportado",
            ahora,
        )
        return HorasReportadas(
            registro.id,
            registro.id_practica,
            registro.semana,
            registro.horas,
            registro.estado,
            registro.fecha,
        )

    def _rechazar(
        self,
        usuario: UsuarioAutenticado,
        id_practica: str,
        ahora: datetime,
    ) -> None:
        """Audita el acceso rechazado y lo niega (ADR-004, ADR-006)."""
        self._bitacora.registrar(
            usuario.id,
            usuario.rol,
            f"practica:{id_practica}",
            "registrar horas",
            ahora,
        )
        raise AccesoDenegado()
