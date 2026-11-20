"""DTO de salida del caso de uso SolicitarActas: un resultado por Practica, en el orden recibido (CU-07)."""

from dataclasses import dataclass

from aplicacion.actas.resultado_solicitud_acta import ResultadoSolicitudActa


@dataclass(frozen=True)
class ActasSolicitadas:
    resultados: tuple[ResultadoSolicitudActa, ...]
