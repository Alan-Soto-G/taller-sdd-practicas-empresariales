"""Caso de uso CU-07 (lado API): el Coordinador solicita las actas finales; la API registra cada acta en generacion y solo la encola (ADR-001, ADR-004, ADR-006)."""

from collections.abc import Callable
from datetime import datetime
from uuid import uuid4

from aplicacion.actas.actas_solicitadas import ActasSolicitadas
from aplicacion.actas.resultado_solicitud_acta import ResultadoSolicitudActa
from aplicacion.actas.solicitud_acta import SolicitudActa
from aplicacion.actas.solicitud_generacion_actas import SolicitudGeneracionActas
from aplicacion.errores.acceso_denegado import AccesoDenegado
from aplicacion.puertos.bitacora import Bitacora
from aplicacion.puertos.publicador_actas import PublicadorActas
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas
from dominio.acta_final import ActaFinal
from dominio.estado_practica import EstadoPractica

ROL_COORDINADOR = "CoordinadorPracticas"


class SolicitarActas:
    """Registra las actas en generacion y publica una SolicitudActa por cada una; nunca compone el PDF."""

    def __init__(
        self,
        repositorio: RepositorioPracticas,
        bitacora: Bitacora,
        publicador: PublicadorActas,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._repositorio = repositorio
        self._bitacora = bitacora
        self._publicador = publicador
        self._reloj = reloj

    def ejecutar(self, solicitud: SolicitudGeneracionActas) -> ActasSolicitadas:
        """Devuelve un resultado por Practica, en el orden recibido."""
        usuario = solicitud.usuario
        ahora = self._reloj()

        if usuario.rol != ROL_COORDINADOR:
            for id_practica in solicitud.ids_practicas:
                self._bitacora.registrar(
                    usuario.id, usuario.rol, f"practica:{id_practica}", "solicitar acta", ahora
                )
            raise AccesoDenegado()

        resultados: list[ResultadoSolicitudActa] = []
        for id_practica in solicitud.ids_practicas:
            practica = self._repositorio.obtener_practica(id_practica)
            if practica is None:
                resultados.append(
                    ResultadoSolicitudActa(id_practica, None, "no solicitada: práctica no encontrada")
                )
                continue
            if practica.estado != EstadoPractica.EVALUADA:
                resultados.append(
                    ResultadoSolicitudActa(id_practica, None, "no solicitada: la práctica no está evaluada")
                )
                continue

            acta = ActaFinal.solicitar(f"AC-{uuid4().hex[:8]}", practica.id, ahora)
            self._repositorio.guardar_acta(acta)
            self._repositorio.guardar_practica(practica.solicitar_acta())
            self._bitacora.registrar(
                usuario.id, usuario.rol, f"acta:{acta.id}", "crear con estado en generación", ahora
            )
            self._bitacora.registrar(
                usuario.id,
                usuario.rol,
                f"practica:{practica.id}",
                "cambiar estado de evaluada a acta en trámite",
                ahora,
            )
            self._publicador.publicar(SolicitudActa(acta.id, practica.id, 1))  # solo encola (ADR-001)
            resultados.append(ResultadoSolicitudActa(id_practica, acta.id, "en generación"))

        return ActasSolicitadas(tuple(resultados))
