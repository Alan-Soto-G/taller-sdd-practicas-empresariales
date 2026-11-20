"""Adaptador de entrada REST de CU-01 a CU-05: traduce POST /postulaciones, POST /plazas, POST /asignaciones, POST /practicas/{id}/horas y POST /registros-horas/{id}/revision a los casos de uso y los errores de aplicacion a la respuesta unificada (ADR-007)."""

from uuid import uuid4

from aplicacion.asignacion.asignar_tutor import AsignarTutor
from aplicacion.asignacion.solicitud_asignacion_tutor import SolicitudAsignacionTutor
from aplicacion.errores.acceso_denegado import AccesoDenegado
from aplicacion.errores.empresa_no_encontrada import EmpresaNoEncontrada
from aplicacion.errores.error_aplicacion import ErrorAplicacion
from aplicacion.errores.no_autenticado import NoAutenticado
from aplicacion.errores.plaza_no_encontrada import PlazaNoEncontrada
from aplicacion.errores.plaza_no_valida import PlazaNoValida
from aplicacion.errores.postulacion_no_permitida import PostulacionNoPermitida
from aplicacion.errores.practica_no_encontrada import PracticaNoEncontrada
from aplicacion.errores.registro_no_encontrado import RegistroNoEncontrado
from aplicacion.errores.registro_no_valido import RegistroNoValido
from aplicacion.errores.tutor_no_encontrado import TutorNoEncontrado
from aplicacion.horas.aprobar_horas import AprobarHoras
from aplicacion.horas.registrar_horas import RegistrarHoras
from aplicacion.horas.solicitud_registro_horas import SolicitudRegistroHoras
from aplicacion.horas.solicitud_revision_horas import SolicitudRevisionHoras
from aplicacion.postulaciones.postularse_plaza import PostularsePlaza
from aplicacion.postulaciones.publicar_plaza import PublicarPlaza
from aplicacion.postulaciones.solicitud_postulacion import SolicitudPostulacion
from aplicacion.postulaciones.solicitud_publicacion_plaza import SolicitudPublicacionPlaza
from infraestructura.validador_token import ValidadorToken

ESTADOS_HTTP: dict[type[ErrorAplicacion], int] = {
    NoAutenticado: 401,
    AccesoDenegado: 403,
    PlazaNoEncontrada: 404,
    EmpresaNoEncontrada: 404,
    TutorNoEncontrado: 404,
    PracticaNoEncontrada: 404,
    RegistroNoEncontrado: 404,
    PlazaNoValida: 400,
    PostulacionNoPermitida: 409,
    RegistroNoValido: 422,
}


class ControladorRest:
    """Controlador REST de postulaciones, plazas, asignaciones, horas y revisiones."""

    def __init__(
        self,
        validador: ValidadorToken,
        postularse_plaza: PostularsePlaza,
        publicar_plaza: PublicarPlaza,
        asignar_tutor: AsignarTutor,
        registrar_horas: RegistrarHoras,
        aprobar_horas: AprobarHoras,
    ) -> None:
        """Inicializa el controlador con sus dependencias."""
        self._validador = validador
        self._postularse_plaza = postularse_plaza
        self._publicar_plaza = publicar_plaza
        self._asignar_tutor = asignar_tutor
        self._registrar_horas = registrar_horas
        self._aprobar_horas = aprobar_horas

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

    def publicar_plaza(
        self,
        token: str | None,
        cuerpo: dict[str, object],
    ) -> tuple[int, dict[str, object]]:
        """Representa la petición POST /plazas."""
        try:
            usuario = self._validador.validar(token)
            solicitud = SolicitudPublicacionPlaza(
                usuario,
                str(cuerpo.get("id_empresa", "")),
                str(cuerpo.get("cargo", "")),
                cuerpo.get("cupos", 0),
                str(cuerpo.get("periodo", "")),
            )
            resultado = self._publicar_plaza.ejecutar(solicitud)
            return (
                201,
                {
                    "id": resultado.id,
                    "id_empresa": resultado.id_empresa,
                    "cargo": resultado.cargo,
                    "cupos": resultado.cupos,
                    "periodo": resultado.periodo,
                    "mensaje": "plaza publicada",
                },
            )
        except ErrorAplicacion as error:
            return self._responder_error(error)

    def asignar_tutor(
        self,
        token: str | None,
        cuerpo: dict[str, object],
    ) -> tuple[int, dict[str, object]]:
        """Representa la petición POST /asignaciones."""
        try:
            usuario = self._validador.validar(token)
            solicitud = SolicitudAsignacionTutor(
                usuario,
                str(cuerpo.get("id_tutor", "")),
                tuple(str(i) for i in cuerpo.get("ids_practicas", [])),
            )
            resultado = self._asignar_tutor.ejecutar(solicitud)
            return (
                200,
                {
                    "id_tutor": resultado.id_tutor,
                    "resultados": [
                        {
                            "id_practica": r.id_practica,
                            "resultado": r.resultado,
                        }
                        for r in resultado.resultados
                    ],
                    "mensaje": "asignación procesada",
                },
            )
        except ErrorAplicacion as error:
            return self._responder_error(error)

    def registrar_horas(
        self,
        token: str | None,
        id_practica: str,
        cuerpo: dict[str, object],
    ) -> tuple[int, dict[str, object]]:
        """Representa la petición POST /practicas/{id}/horas."""
        try:
            usuario = self._validador.validar(token)
            solicitud = SolicitudRegistroHoras(
                usuario,
                id_practica,
                str(cuerpo.get("semana", "")),
                cuerpo.get("horas", 0),
                str(cuerpo.get("actividades", "")),
            )
            resultado = self._registrar_horas.ejecutar(solicitud)
            return (
                201,
                {
                    "id": resultado.id,
                    "id_practica": resultado.id_practica,
                    "semana": resultado.semana,
                    "horas": resultado.horas,
                    "estado": str(resultado.estado),
                    "fecha": resultado.fecha.isoformat(),
                    "mensaje": "horas reportadas, pendientes de aprobación del tutor",
                },
            )
        except ErrorAplicacion as error:
            return self._responder_error(error)

    def revisar_horas(
        self,
        token: str | None,
        id_registro: str,
        cuerpo: dict[str, object],
    ) -> tuple[int, dict[str, object]]:
        """Representa la petición POST /registros-horas/{id}/revision."""
        try:
            usuario = self._validador.validar(token)
            solicitud = SolicitudRevisionHoras(
                usuario,
                id_registro,
                str(cuerpo.get("decision", "")),
            )
            resultado = self._aprobar_horas.ejecutar(solicitud)
            mensaje = "horas aprobadas" if str(resultado.estado) == "aprobado" else "horas rechazadas"
            return (
                200,
                {
                    "id": resultado.id,
                    "id_practica": resultado.id_practica,
                    "estado": str(resultado.estado),
                    "horas_aprobadas": resultado.horas_aprobadas,
                    "estado_practica": str(resultado.estado_practica),
                    "mensaje": mensaje,
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
        if isinstance(error, (PostulacionNoPermitida, PlazaNoValida, RegistroNoValido)):
            cuerpo["motivo"] = error.motivo
        return (estado, cuerpo)
