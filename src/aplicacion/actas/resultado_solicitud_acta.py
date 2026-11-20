"""DTO con el resultado de solicitar el acta de una Practica: 'en generación' o 'no solicitada: <motivo>' (CU-07)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoSolicitudActa:
    id_practica: str
    id_acta: str | None
    resultado: str
