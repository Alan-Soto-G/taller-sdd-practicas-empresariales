"""Caso de uso CU-05: el Tutor asignado aprueba o rechaza un RegistroHoras (EAC-04; ADR-004, ADR-006, ADR-007, ADR-008)."""

from collections.abc import Callable
from datetime import datetime

from aplicacion.configuracion.consultar_horas_requeridas import ConsultarHorasRequeridas
from aplicacion.errores.acceso_denegado import AccesoDenegado
from aplicacion.errores.registro_no_encontrado import RegistroNoEncontrado
from aplicacion.errores.registro_no_valido import RegistroNoValido
from aplicacion.horas.horas_revisadas import HorasRevisadas
from aplicacion.horas.solicitud_revision_horas import SolicitudRevisionHoras
from aplicacion.puertos.bitacora import Bitacora
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas
from aplicacion.usuario_autenticado import UsuarioAutenticado
from dominio.estado_practica import EstadoPractica
from dominio.estado_registro_horas import EstadoRegistroHoras


ROL_TUTOR = "Tutor"
APROBAR = "aprobar"
RECHAZAR = "rechazar"


class AprobarHoras:
    """Revisa un RegistroHoras reportado y, al aprobar, completa la Practica si alcanza las horas requeridas."""

    def __init__(
        self,
        repositorio: RepositorioPracticas,
        bitacora: Bitacora,
        consultar_horas: ConsultarHorasRequeridas,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._repositorio = repositorio
        self._bitacora = bitacora
        self._consultar_horas = consultar_horas
        self._reloj = reloj

    def ejecutar(self, solicitud: SolicitudRevisionHoras) -> HorasRevisadas:
        """Aprueba o rechaza el registro y devuelve el resultado."""
        usuario = solicitud.usuario
        ahora = self._reloj()

        if usuario.rol != ROL_TUTOR:
            self._rechazar(usuario, solicitud.id_registro, ahora)

        registro = self._repositorio.obtener_registro_horas(solicitud.id_registro)
        if registro is None:
            raise RegistroNoEncontrado(solicitud.id_registro)

        practica = self._repositorio.obtener_practica(registro.id_practica)
        if practica is None or practica.id_tutor != usuario.id:
            self._rechazar(usuario, registro.id, ahora)

        if solicitud.decision not in (APROBAR, RECHAZAR):
            raise RegistroNoValido("la decisión debe ser aprobar o rechazar")

        if registro.estado != EstadoRegistroHoras.REPORTADO:
            raise RegistroNoValido("el registro ya fue revisado")

        revisado = (
            registro.aprobar()
            if solicitud.decision == APROBAR
            else registro.rechazar()
        )
        self._repositorio.actualizar_registro_horas(revisado)
        self._bitacora.registrar(
            usuario.id,
            usuario.rol,
            f"registro_horas:{revisado.id}",
            f"cambiar estado de reportado a {revisado.estado}",
            ahora,
        )

        horas = self._repositorio.sumar_horas_aprobadas(practica.id)
        if (
            revisado.estado == EstadoRegistroHoras.APROBADO
            and practica.estado == EstadoPractica.EN_CURSO
            and horas >= self._consultar_horas.ejecutar(practica.version_regla)
        ):
            practica = practica.completar_horas()
            self._repositorio.guardar_practica(practica)
            self._bitacora.registrar(
                usuario.id,
                usuario.rol,
                f"practica:{practica.id}",
                "cambiar estado de en curso a horas completas",
                ahora,
            )

        return HorasRevisadas(
            revisado.id,
            revisado.id_practica,
            revisado.estado,
            horas,
            practica.estado,
        )

    def _rechazar(
        self,
        usuario: UsuarioAutenticado,
        id_registro: str,
        ahora: datetime,
    ) -> None:
        """Audita el acceso rechazado y lo niega (ADR-004, ADR-006)."""
        self._bitacora.registrar(
            usuario.id,
            usuario.rol,
            f"registro_horas:{id_registro}",
            "aprobar horas",
            ahora,
        )
        raise AccesoDenegado()
