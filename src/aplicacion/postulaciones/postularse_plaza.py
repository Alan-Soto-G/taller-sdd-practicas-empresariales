"""Caso de uso CU-01: el Estudiante se postula a una Plaza (ADR-004, ADR-006, ADR-007)."""

from collections.abc import Callable
from datetime import datetime
from uuid import uuid4

from aplicacion.errores.acceso_denegado import AccesoDenegado
from aplicacion.errores.plaza_no_encontrada import PlazaNoEncontrada
from aplicacion.errores.postulacion_no_permitida import PostulacionNoPermitida
from aplicacion.postulaciones.postulacion_enviada import PostulacionEnviada
from aplicacion.postulaciones.solicitud_postulacion import SolicitudPostulacion
from aplicacion.puertos.bitacora import Bitacora
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas
from dominio.postulacion import Postulacion


ROL_ESTUDIANTE = "Estudiante"


class PostularsePlaza:
    """Permite a un estudiante postularse a una plaza disponible."""

    def __init__(
        self,
        repositorio: RepositorioPracticas,
        bitacora: Bitacora,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._repositorio = repositorio
        self._bitacora = bitacora
        self._reloj = reloj

    def ejecutar(self, solicitud: SolicitudPostulacion) -> PostulacionEnviada:
        """Ejecuta la postulación y devuelve su resultado."""
        usuario = solicitud.usuario
        ahora = self._reloj()

        if usuario.rol != ROL_ESTUDIANTE:
            self._bitacora.registrar(
                usuario.id,
                usuario.rol,
                f"plaza:{solicitud.id_plaza}",
                "postularse",
                ahora,
            )
            raise AccesoDenegado()

        plaza = self._repositorio.obtener_plaza(solicitud.id_plaza)
        if plaza is None:
            raise PlazaNoEncontrada(solicitud.id_plaza)

        if self._repositorio.existe_postulacion(usuario.id, plaza.id):
            raise PostulacionNoPermitida("ya te postulaste a esta plaza")

        if self._repositorio.tiene_postulacion_aceptada_en_periodo(
            usuario.id, plaza.periodo
        ):
            raise PostulacionNoPermitida(
                "ya tienes una postulación aceptada en el periodo"
            )

        if not plaza.tiene_cupo(
            self._repositorio.contar_postulaciones_aceptadas(plaza.id)
        ):
            raise PostulacionNoPermitida("la plaza no tiene cupos disponibles")

        postulacion = Postulacion.enviar(
            f"PO-{uuid4().hex[:8]}",
            usuario.id,
            plaza.id,
            plaza.periodo,
            ahora.date(),
        )
        self._repositorio.guardar_postulacion(postulacion)
        self._bitacora.registrar(
            usuario.id,
            usuario.rol,
            f"postulacion:{postulacion.id}",
            "crear con estado enviada",
            ahora,
        )
        return PostulacionEnviada(
            postulacion.id,
            postulacion.id_plaza,
            postulacion.estado,
            postulacion.fecha,
        )
