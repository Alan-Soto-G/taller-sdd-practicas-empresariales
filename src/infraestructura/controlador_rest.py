"""Adaptador de entrada REST de CU-01: traduce la peticion POST /postulaciones al caso de uso y los errores de aplicacion a la respuesta unificada (ADR-007)."""

from uuid import uuid4

from aplicacion.errores.acceso_denegado import AccesoDenegado
from aplicacion.errores.error_aplicacion import ErrorAplicacion
from aplicacion.errores.no_autenticado import NoAutenticado
from aplicacion.errores.plaza_no_encontrada import PlazaNoEncontrada
from aplicacion.errores.postulacion_no_permitida import PostulacionNoPermitida
from aplicacion.postulaciones.postularse_plaza import PostularsePlaza
from aplicacion.postulaciones.solicitud_postulacion import SolicitudPostulacion
from infraestructura.validador_token import ValidadorToken

ESTADOS_HTTP: dict[type[ErrorAplicacion], int] = {
    NoAutenticado: 401,
    AccesoDenegado: 403,
    PlazaNoEncontrada: 404,
    PostulacionNoPermitida: 409,
}


class ControladorRest:
    """Controlador REST para la gestión de postulaciones a plazas."""

    def __init__(
        self,
        validador: ValidadorToken,
        postularse_plaza: PostularsePlaza,
    ) -> None:
        """Inicializa el controlador con sus dependencias."""
        self._validador = validador
        self._postularse_plaza = postularse_plaza

    def postular(
        self,
        token: str | None,
        cuerpo: dict[str, str],
    ) -> tuple[int, dict[str, object]]:
        """Representa la petición POST /postulaciones."""
        try:
            usuario = self._validador.validar(token)
            solicitud = SolicitudPostulacion(usuario, cuerpo.get("id_plaza", ""))
            resultado = self._postularse_plaza.ejecutar(solicitud)
            return (
                201,
                {
                    "id": resultado.id,
                    "id_plaza": resultado.id_plaza,
                    "estado": str(resultado.estado),
                    "fecha": resultado.fecha.isoformat(),
                    "mensaje": "postulación enviada",
                },
            )
        except ErrorAplicacion as error:
            return self._responder_error(error)

    def _responder_error(
        self,
        error: ErrorAplicacion,
    ) -> tuple[int, dict[str, object]]:
        """Traduce un error de aplicación a la estructura de respuesta unificada."""
        estado = ESTADOS_HTTP.get(type(error), 500)
        cuerpo: dict[str, object] = {
            "codigo": error.codigo,
            "mensaje": error.mensaje,
            "correlacion": uuid4().hex,
        }
        if isinstance(error, PostulacionNoPermitida):
            cuerpo["motivo"] = error.motivo
        return (estado, cuerpo)
