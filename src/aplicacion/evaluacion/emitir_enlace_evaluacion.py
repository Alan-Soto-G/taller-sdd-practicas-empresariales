"""Caso de uso CU-06 (paso 1): el Coordinador emite el enlace de evaluacion de una Practica con horas completas y lo envia al Representante de la Empresa (ADR-004, ADR-005, ADR-006, ADR-007)."""

import secrets
from collections.abc import Callable
from datetime import datetime
from uuid import uuid4

from aplicacion.errores.acceso_denegado import AccesoDenegado
from aplicacion.errores.correo_no_enviado import CorreoNoEnviado
from aplicacion.errores.evaluacion_no_permitida import EvaluacionNoPermitida
from aplicacion.errores.practica_no_encontrada import PracticaNoEncontrada
from aplicacion.evaluacion.enlace_emitido import EnlaceEmitido
from aplicacion.evaluacion.solicitud_enlace_evaluacion import (
    SolicitudEnlaceEvaluacion,
)
from aplicacion.puertos.bitacora import Bitacora
from aplicacion.puertos.notificador import Notificador
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas
from dominio.enlace_acceso import EnlaceAcceso
from dominio.estado_practica import EstadoPractica


ROL_COORDINADOR = "CoordinadorPracticas"
ACCION_EVALUAR = "evaluar"


class EmitirEnlaceEvaluacion:
    """Emite un EnlaceAcceso de un solo uso para evaluar y lo envia al correo del Representante."""

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

    def ejecutar(self, solicitud: SolicitudEnlaceEvaluacion) -> EnlaceEmitido:
        """Emite el enlace, invalida el anterior y lo envia por correo."""
        usuario = solicitud.usuario
        ahora = self._reloj()

        if usuario.rol != ROL_COORDINADOR:
            self._bitacora.registrar(
                usuario.id,
                usuario.rol,
                f"practica:{solicitud.id_practica}",
                "emitir enlace de evaluación",
                ahora,
            )
            raise AccesoDenegado()

        practica = self._repositorio.obtener_practica(solicitud.id_practica)
        if practica is None:
            raise PracticaNoEncontrada(solicitud.id_practica)

        if practica.estado != EstadoPractica.HORAS_COMPLETAS:
            raise EvaluacionNoPermitida("la práctica no tiene las horas completas")

        representante = self._repositorio.obtener_representante_de_empresa(
            practica.id_empresa
        )
        if representante is None:
            raise EvaluacionNoPermitida(
                "la empresa no tiene representante registrado"
            )

        self._repositorio.invalidar_enlaces(
            practica.id, ACCION_EVALUAR
        )  # reemitir invalida el anterior, ADR-005
        enlace = EnlaceAcceso.emitir(
            f"EN-{uuid4().hex[:8]}",
            secrets.token_urlsafe(16),
            practica.id,
            representante.id,
            ACCION_EVALUAR,
            ahora,
        )
        self._repositorio.guardar_enlace(enlace)

        try:
            self._notificador.enviar(
                [representante.correo],
                "Evaluación del practicante",
                f"Evalúe a su practicante en /evaluaciones/{enlace.token}; "
                f"el enlace vence el {enlace.vence:%Y-%m-%d}.",
            )
        except CorreoNoEnviado:
            pass  # el enlace queda guardado y el correo pendiente de reenvio, ADR-007

        return EnlaceEmitido(
            enlace.id,
            practica.id,
            enlace.vence,
            representante.correo,
        )
