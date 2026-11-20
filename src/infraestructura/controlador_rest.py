"""Adaptador de entrada REST de CU-01 a CU-08: traduce las peticiones HTTP a los casos de uso y los errores de aplicacion a la respuesta unificada (ADR-007). Los usuarios institucionales entran con token (ADR-004) y el Representante de la Empresa con enlace (ADR-005)."""

from uuid import uuid4

from aplicacion.actas.aprobacion_registrada import AprobacionRegistrada
from aplicacion.actas.aprobar_acta import AprobarActa
from aplicacion.actas.emitir_enlace_aprobacion import EmitirEnlaceAprobacion
from aplicacion.actas.solicitar_actas import SolicitarActas
from aplicacion.actas.solicitud_aprobacion_acta import SolicitudAprobacionActa
from aplicacion.actas.solicitud_enlace_aprobacion import SolicitudEnlaceAprobacion
from aplicacion.actas.solicitud_generacion_actas import SolicitudGeneracionActas
from aplicacion.asignacion.asignar_tutor import AsignarTutor
from aplicacion.asignacion.solicitud_asignacion_tutor import SolicitudAsignacionTutor
from aplicacion.errores.acceso_denegado import AccesoDenegado
from aplicacion.errores.acta_no_encontrada import ActaNoEncontrada
from aplicacion.errores.aprobacion_no_permitida import AprobacionNoPermitida
from aplicacion.errores.enlace_no_valido import EnlaceNoValido
from aplicacion.errores.empresa_no_encontrada import EmpresaNoEncontrada
from aplicacion.errores.error_aplicacion import ErrorAplicacion
from aplicacion.errores.evaluacion_no_permitida import EvaluacionNoPermitida
from aplicacion.errores.evaluacion_no_valida import EvaluacionNoValida
from aplicacion.errores.no_autenticado import NoAutenticado
from aplicacion.errores.plaza_no_encontrada import PlazaNoEncontrada
from aplicacion.errores.plaza_no_valida import PlazaNoValida
from aplicacion.errores.postulacion_no_permitida import PostulacionNoPermitida
from aplicacion.errores.practica_no_encontrada import PracticaNoEncontrada
from aplicacion.errores.registro_no_encontrado import RegistroNoEncontrado
from aplicacion.errores.registro_no_valido import RegistroNoValido
from aplicacion.errores.tutor_no_encontrado import TutorNoEncontrado
from aplicacion.evaluacion.consultar_formulario_evaluacion import ConsultarFormularioEvaluacion
from aplicacion.evaluacion.emitir_enlace_evaluacion import EmitirEnlaceEvaluacion
from aplicacion.evaluacion.intento_enlace_rechazado import IntentoEnlaceRechazado
from aplicacion.evaluacion.registrar_enlace_rechazado import RegistrarEnlaceRechazado
from aplicacion.evaluacion.registrar_evaluacion import RegistrarEvaluacion
from aplicacion.evaluacion.solicitud_enlace_evaluacion import SolicitudEnlaceEvaluacion
from aplicacion.evaluacion.solicitud_evaluacion import SolicitudEvaluacion
from aplicacion.horas.aprobar_horas import AprobarHoras
from aplicacion.horas.registrar_horas import RegistrarHoras
from aplicacion.horas.solicitud_registro_horas import SolicitudRegistroHoras
from aplicacion.horas.solicitud_revision_horas import SolicitudRevisionHoras
from aplicacion.identidad_enlace import IdentidadEnlace
from aplicacion.postulaciones.postularse_plaza import PostularsePlaza
from aplicacion.postulaciones.publicar_plaza import PublicarPlaza
from aplicacion.postulaciones.solicitud_postulacion import SolicitudPostulacion
from aplicacion.postulaciones.solicitud_publicacion_plaza import SolicitudPublicacionPlaza
from infraestructura.validador_enlace import ValidadorEnlace
from infraestructura.validador_token import ValidadorToken

ACCION_EVALUAR = "evaluar"
ACCION_APROBAR_ACTA = "aprobar acta"

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
    EnlaceNoValido: 410,
    EvaluacionNoPermitida: 409,
    EvaluacionNoValida: 422,
    ActaNoEncontrada: 404,
    AprobacionNoPermitida: 409,
}


class ControladorRest:
    """Controlador REST de postulaciones, plazas, asignaciones, horas, evaluaciones y actas."""

    def __init__(
        self,
        validador: ValidadorToken,
        postularse_plaza: PostularsePlaza,
        publicar_plaza: PublicarPlaza,
        asignar_tutor: AsignarTutor,
        registrar_horas: RegistrarHoras,
        aprobar_horas: AprobarHoras,
        validador_enlace: ValidadorEnlace,
        emitir_enlace_evaluacion: EmitirEnlaceEvaluacion,
        consultar_formulario_evaluacion: ConsultarFormularioEvaluacion,
        registrar_evaluacion: RegistrarEvaluacion,
        solicitar_actas: SolicitarActas,
        emitir_enlace_aprobacion: EmitirEnlaceAprobacion,
        aprobar_acta: AprobarActa,
        registrar_enlace_rechazado: RegistrarEnlaceRechazado,
    ) -> None:
        """Inicializa el controlador con sus dependencias."""
        self._validador = validador
        self._postularse_plaza = postularse_plaza
        self._publicar_plaza = publicar_plaza
        self._asignar_tutor = asignar_tutor
        self._registrar_horas = registrar_horas
        self._aprobar_horas = aprobar_horas
        self._validador_enlace = validador_enlace
        self._emitir_enlace_evaluacion = emitir_enlace_evaluacion
        self._consultar_formulario_evaluacion = consultar_formulario_evaluacion
        self._registrar_evaluacion = registrar_evaluacion
        self._solicitar_actas = solicitar_actas
        self._emitir_enlace_aprobacion = emitir_enlace_aprobacion
        self._aprobar_acta = aprobar_acta
        self._registrar_enlace_rechazado = registrar_enlace_rechazado

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

    def emitir_enlace_evaluacion(
        self,
        token: str | None,
        id_practica: str,
    ) -> tuple[int, dict[str, object]]:
        """Representa la petición POST /practicas/{id}/enlaces-evaluacion."""
        try:
            usuario = self._validador.validar(token)
            resultado = self._emitir_enlace_evaluacion.ejecutar(
                SolicitudEnlaceEvaluacion(usuario, id_practica)
            )
            return (
                201,
                {
                    "id_enlace": resultado.id_enlace,
                    "id_practica": resultado.id_practica,
                    "vence": resultado.vence.isoformat(),
                    "correo_representante": resultado.correo_representante,
                    "mensaje": "enlace de evaluación enviado",
                },
            )
        except ErrorAplicacion as error:
            return self._responder_error(error)

    def abrir_evaluacion(
        self,
        enlace: str,
    ) -> tuple[int, dict[str, object]]:
        """Representa la petición GET /evaluaciones/{enlace}; no pide token institucional (ADR-005)."""
        try:
            identidad = self._validar_enlace(enlace, ACCION_EVALUAR)
            formulario = self._consultar_formulario_evaluacion.ejecutar(identidad)
            return (
                200,
                {
                    "id_practica": formulario.id_practica,
                    "id_estudiante": formulario.id_estudiante,
                    "criterios": [
                        {"nombre": c.nombre, "escala": c.escala}
                        for c in formulario.criterios
                    ],
                },
            )
        except ErrorAplicacion as error:
            return self._responder_error(error)

    def enviar_evaluacion(
        self,
        enlace: str,
        cuerpo: dict[str, object],
    ) -> tuple[int, dict[str, object]]:
        """Representa la petición POST /evaluaciones/{enlace}; no pide token institucional (ADR-005)."""
        try:
            identidad = self._validar_enlace(enlace, ACCION_EVALUAR)
            solicitud = SolicitudEvaluacion(
                identidad,
                dict(cuerpo.get("calificaciones", {})),
                str(cuerpo.get("observaciones", "")),
            )
            resultado = self._registrar_evaluacion.ejecutar(solicitud)
            return (
                201,
                {
                    "id": resultado.id,
                    "id_practica": resultado.id_practica,
                    "estado_practica": str(resultado.estado_practica),
                    "mensaje": "evaluación enviada",
                },
            )
        except ErrorAplicacion as error:
            return self._responder_error(error)

    def solicitar_actas(
        self,
        token: str | None,
        cuerpo: dict[str, object],
    ) -> tuple[int, dict[str, object]]:
        """Representa la petición POST /actas; responde 202 porque el Worker de actas genera las actas después (ADR-001)."""
        try:
            usuario = self._validador.validar(token)
            solicitud = SolicitudGeneracionActas(
                usuario,
                tuple(str(i) for i in cuerpo.get("ids_practicas", [])),
            )
            resultado = self._solicitar_actas.ejecutar(solicitud)
            return (
                202,
                {
                    "resultados": [
                        {
                            "id_practica": r.id_practica,
                            "id_acta": r.id_acta,
                            "resultado": r.resultado,
                        }
                        for r in resultado.resultados
                    ],
                    "mensaje": "actas en generación; se le notificará",
                },
            )
        except ErrorAplicacion as error:
            return self._responder_error(error)

    def emitir_enlace_aprobacion(
        self,
        token: str | None,
        id_acta: str,
    ) -> tuple[int, dict[str, object]]:
        """Representa la petición POST /actas/{id}/enlaces-aprobacion."""
        try:
            usuario = self._validador.validar(token)
            resultado = self._emitir_enlace_aprobacion.ejecutar(
                SolicitudEnlaceAprobacion(usuario, id_acta)
            )
            return (
                201,
                {
                    "id_enlace": resultado.id_enlace,
                    "id_practica": resultado.id_practica,
                    "vence": resultado.vence.isoformat(),
                    "correo_representante": resultado.correo_representante,
                    "mensaje": "enlace de aprobación enviado",
                },
            )
        except ErrorAplicacion as error:
            return self._responder_error(error)

    def aprobar_acta(
        self,
        token: str | None,
        id_acta: str,
    ) -> tuple[int, dict[str, object]]:
        """Representa la petición POST /actas/{id}/aprobaciones del Tutor o del Coordinador."""
        try:
            usuario = self._validador.validar(token)
            resultado = self._aprobar_acta.aprobar_con_token(
                SolicitudAprobacionActa(usuario, id_acta)
            )
            return (201, self._cuerpo_aprobacion(resultado))
        except ErrorAplicacion as error:
            return self._responder_error(error)

    def aprobar_acta_con_enlace(
        self,
        enlace: str,
    ) -> tuple[int, dict[str, object]]:
        """Representa la petición POST /aprobaciones-acta/{enlace}; no pide token institucional (ADR-005)."""
        try:
            identidad = self._validar_enlace(enlace, ACCION_APROBAR_ACTA)
            resultado = self._aprobar_acta.aprobar_con_enlace(identidad)
            return (201, self._cuerpo_aprobacion(resultado))
        except ErrorAplicacion as error:
            return self._responder_error(error)

    def _validar_enlace(self, enlace: str, accion: str) -> IdentidadEnlace:
        """Valida el enlace; si se rechaza, el caso de uso audita el intento antes de responder (ADR-005, ADR-006)."""
        try:
            return self._validador_enlace.validar(enlace, accion)
        except EnlaceNoValido as error:
            self._registrar_enlace_rechazado.ejecutar(
                IntentoEnlaceRechazado(error.id_enlace, error.id_representante, error.motivo)
            )
            raise

    def _cuerpo_aprobacion(self, resultado: AprobacionRegistrada) -> dict[str, object]:
        """Arma la respuesta de una aprobación registrada."""
        return {
            "id_acta": resultado.id_acta,
            "rol": resultado.rol,
            "aprobaciones": resultado.aprobaciones,
            "estado_acta": str(resultado.estado_acta),
            "estado_practica": str(resultado.estado_practica),
            "mensaje": "aprobación registrada",
        }

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
        if isinstance(
            error,
            (
                PostulacionNoPermitida,
                PlazaNoValida,
                RegistroNoValido,
                EnlaceNoValido,
                EvaluacionNoPermitida,
                EvaluacionNoValida,
                AprobacionNoPermitida,
            ),
        ):
            cuerpo["motivo"] = error.motivo
        return (estado, cuerpo)
