"""Caso de uso CU-08: el Tutor asignado, el Representante (con enlace) y el Coordinador aprueban el acta generada; con las tres aprobaciones el acta queda aprobada y la Practica cerrada (ADR-004, ADR-005, ADR-006)."""

from collections.abc import Callable
from datetime import datetime

from aplicacion.actas.aprobacion_registrada import AprobacionRegistrada
from aplicacion.actas.solicitud_aprobacion_acta import SolicitudAprobacionActa
from aplicacion.errores.acceso_denegado import AccesoDenegado
from aplicacion.errores.acta_no_encontrada import ActaNoEncontrada
from aplicacion.errores.aprobacion_no_permitida import AprobacionNoPermitida
from aplicacion.errores.enlace_no_valido import EnlaceNoValido
from aplicacion.identidad_enlace import IdentidadEnlace
from aplicacion.puertos.bitacora import Bitacora
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas
from dominio.acta_final import ActaFinal
from dominio.aprobacion import APROBACIONES_REQUERIDAS, Aprobacion
from dominio.estado_acta import EstadoActa
from dominio.practica import Practica

ROL_TUTOR = "Tutor"
ROL_COORDINADOR = "CoordinadorPracticas"
ROL_REPRESENTANTE = "RepresentanteEmpresa"


class AprobarActa:
    """Registra las aprobaciones electronicas del acta; reemplazan las firmas manuales (OB-03)."""

    def __init__(
        self,
        repositorio: RepositorioPracticas,
        bitacora: Bitacora,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._repositorio = repositorio
        self._bitacora = bitacora
        self._reloj = reloj

    def aprobar_con_token(self, solicitud: SolicitudAprobacionActa) -> AprobacionRegistrada:
        """Aprobacion del Tutor asignado o del Coordinador (ADR-004)."""
        usuario = solicitud.usuario
        ahora = self._reloj()
        acta = self._repositorio.obtener_acta(solicitud.id_acta)
        if acta is None:
            raise ActaNoEncontrada(solicitud.id_acta)
        practica = self._repositorio.obtener_practica(acta.id_practica)

        autorizado = usuario.rol == ROL_COORDINADOR or (
            usuario.rol == ROL_TUTOR and practica.id_tutor == usuario.id
        )
        if not autorizado:
            self._bitacora.registrar(usuario.id, usuario.rol, f"acta:{acta.id}", "aprobar acta", ahora)
            raise AccesoDenegado()

        self._validar(acta, usuario.rol)
        return self._registrar(acta, practica, usuario.rol, usuario.id, ahora)

    def aprobar_con_enlace(self, identidad: IdentidadEnlace) -> AprobacionRegistrada:
        """Aprobacion del Representante con el enlace 'aprobar acta' ya validado (ADR-005)."""
        ahora = self._reloj()
        acta = self._repositorio.obtener_acta_de_practica(identidad.id_practica)
        if acta is None:
            raise ActaNoEncontrada(identidad.id_practica)
        practica = self._repositorio.obtener_practica(acta.id_practica)

        self._validar(acta, ROL_REPRESENTANTE)
        if not self._repositorio.marcar_enlace_usado(identidad.id_enlace):
            raise EnlaceNoValido("enlace usado")  # un solo uso (ADR-005)
        self._bitacora.registrar(
            identidad.id_representante,
            ROL_REPRESENTANTE,
            f"enlace:{identidad.id_enlace}",
            "usar enlace de aprobación",
            ahora,
        )
        return self._registrar(acta, practica, ROL_REPRESENTANTE, identidad.id_representante, ahora)

    def _validar(self, acta: ActaFinal, rol: str) -> None:
        """Reglas de CU-08: solo un acta generada, y cada rol aprueba una vez."""
        if acta.estado != EstadoActa.GENERADA:
            raise AprobacionNoPermitida("el acta no está generada")
        if any(a.rol == rol for a in self._repositorio.listar_aprobaciones(acta.id)):
            raise AprobacionNoPermitida(f"el rol {rol} ya aprobó el acta")

    def _registrar(
        self, acta: ActaFinal, practica: Practica, rol: str, id_usuario: str, ahora: datetime
    ) -> AprobacionRegistrada:
        """Guarda y audita la Aprobacion; con la tercera, aprueba el acta y cierra la Practica (ADR-006)."""
        self._repositorio.guardar_aprobacion(Aprobacion(acta.id, rol, id_usuario, ahora))
        self._bitacora.registrar(id_usuario, rol, f"acta:{acta.id}", "aprobar acta", ahora)

        aprobaciones = len(self._repositorio.listar_aprobaciones(acta.id))
        if aprobaciones >= APROBACIONES_REQUERIDAS:
            acta = acta.aprobar()
            self._repositorio.guardar_acta(acta)
            self._bitacora.registrar(
                id_usuario, rol, f"acta:{acta.id}", "cambiar estado de generada a aprobada", ahora
            )
            practica = practica.cerrar()
            self._repositorio.guardar_practica(practica)
            self._bitacora.registrar(
                id_usuario, rol, f"practica:{practica.id}", "cambiar estado de acta en trámite a cerrada", ahora
            )

        return AprobacionRegistrada(acta.id, rol, aprobaciones, acta.estado, practica.estado)
