"""DTO con el resultado de un intento del Worker: generada, reintentar (con su espera), con error u omitida (CU-07, ADR-001)."""

from dataclasses import dataclass
from datetime import timedelta


@dataclass(frozen=True)
class ResultadoGeneracion:
    id_acta: str
    estado: str
    espera: timedelta | None = None
