"""Caso de uso CU-08: el Coordinador emite el enlace de un solo uso para que el Representante apruebe el acta generada (ADR-004, ADR-005, ADR-007)."""

import secrets
from collections.abc import Callable
from datetime import datetime
from uuid import uuid4

from aplicacion.actas.solicitud_enlace_aprobacion import SolicitudEnlaceAprobacion
from aplicacion.errores.acceso_denegado import AccesoDenegado
from aplicacion.errores.acta_no_encontrada import ActaNoEncontrada
from aplicacion.errores.aprobacion_no_permitida import AprobacionNoPermitida
from aplicacion.errores.correo_no_enviado import CorreoNoEnviado
from aplicacion.evaluacion.enlace_emitido import EnlaceEmitido
from aplicacion.puertos.bitacora import Bitacora
from aplicacion.puertos.notificador import Notificador
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas
from dominio.enlace_acceso import EnlaceAcceso
from dominio.estado_acta import EstadoActa

ROL_COORDINADOR = "CoordinadorPracticas"
ACCION_APROBAR_ACTA = "aprobar acta"


class EmitirEnlaceAprobacion:
    """Emite el EnlaceAcceso 'aprobar acta', invalida el anterior y lo envia al Representante."""

    def __init__(
        self,
        repositorio: RepositorioPracticas,
        bitacora: Bitacora,
        notificador: Notificador,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._repositorio = repositorio
        self._bitacora = bitacora
        self._notificador = notificador
        self._reloj = reloj

    def ejecutar(self, solicitud: SolicitudEnlaceAprobacion) -> EnlaceEmitido:
        """Emite el enlace de aprobacion del acta y lo envia por correo."""
        usuario = solicitud.usuario
        ahora = self._reloj()

        if usuario.rol != ROL_COORDINADOR:
            self._bitacora.registrar(
                usuario.id, usuario.rol, f"acta:{solicitud.id_acta}", "emitir enlace de aprobación", ahora
            )
            raise AccesoDenegado()

        acta = self._repositorio.obtener_acta(solicitud.id_acta)
        if acta is None:
            raise ActaNoEncontrada(solicitud.id_acta)
        if acta.estado != EstadoActa.GENERADA:
            raise AprobacionNoPermitida("el acta no está generada")

        practica = self._repositorio.obtener_practica(acta.id_practica)
        representante = self._repositorio.obtener_representante_de_empresa(practica.id_empresa)
        if representante is None:
            raise AprobacionNoPermitida("la empresa no tiene representante registrado")

        self._repositorio.invalidar_enlaces(practica.id, ACCION_APROBAR_ACTA)  # reemitir invalida el anterior (ADR-005)
        enlace = EnlaceAcceso.emitir(
            f"EN-{uuid4().hex[:8]}",
            secrets.token_urlsafe(16),
            practica.id,
            representante.id,
            ACCION_APROBAR_ACTA,
            ahora,
        )
        self._repositorio.guardar_enlace(enlace)

        try:
            self._notificador.enviar(
                [representante.correo],
                "Aprobación del acta final",
                f"Apruebe el acta {acta.id} en /aprobaciones-acta/{enlace.token}; "
                f"el enlace vence el {enlace.vence:%Y-%m-%d}.",
            )
        except CorreoNoEnviado:
            pass  # el enlace queda guardado y el correo pendiente de reenvio (ADR-007)

        return EnlaceEmitido(enlace.id, practica.id, enlace.vence, representante.correo)
