"""Caso de uso CU-02: el Coordinador de Practicas publica una Plaza (ADR-004, ADR-006, ADR-007)."""

from collections.abc import Callable
from datetime import datetime
from uuid import uuid4

from aplicacion.errores.acceso_denegado import AccesoDenegado
from aplicacion.errores.empresa_no_encontrada import EmpresaNoEncontrada
from aplicacion.errores.plaza_no_valida import PlazaNoValida
from aplicacion.postulaciones.plaza_publicada import PlazaPublicada
from aplicacion.postulaciones.solicitud_publicacion_plaza import SolicitudPublicacionPlaza
from aplicacion.puertos.bitacora import Bitacora
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas
from dominio.plaza import Plaza


ROL_COORDINADOR = "CoordinadorPracticas"


class PublicarPlaza:
    """Permite al Coordinador de Practicas publicar una Plaza."""

    def __init__(
        self,
        repositorio: RepositorioPracticas,
        bitacora: Bitacora,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._repositorio = repositorio
        self._bitacora = bitacora
        self._reloj = reloj

    def ejecutar(
        self, solicitud: SolicitudPublicacionPlaza
    ) -> PlazaPublicada:
        """Ejecuta la publicación y devuelve la Plaza publicada."""
        usuario = solicitud.usuario
        ahora = self._reloj()

        if usuario.rol != ROL_COORDINADOR:
            self._bitacora.registrar(
                usuario.id,
                usuario.rol,
                f"empresa:{solicitud.id_empresa}",
                "publicar plaza",
                ahora,
            )
            raise AccesoDenegado()

        if self._repositorio.obtener_empresa(solicitud.id_empresa) is None:
            raise EmpresaNoEncontrada(solicitud.id_empresa)

        motivo = Plaza.motivo_invalidez(
            solicitud.cargo,
            solicitud.cupos,
            solicitud.periodo,
        )
        if motivo is not None:
            raise PlazaNoValida(motivo)

        plaza = Plaza(
            f"PL-{uuid4().hex[:8]}",
            solicitud.id_empresa,
            solicitud.cargo,
            solicitud.cupos,
            solicitud.periodo,
        )
        self._repositorio.guardar_plaza(plaza)
        return PlazaPublicada(
            plaza.id,
            plaza.id_empresa,
            plaza.cargo,
            plaza.cupos,
            plaza.periodo,
        )
