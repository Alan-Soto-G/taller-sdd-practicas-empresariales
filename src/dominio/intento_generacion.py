"""IntentoGeneracion: cada intento del Worker de actas de componer el PDF; maximo 3 por acta (vista logica, ADR-001)."""

from dataclasses import dataclass
from datetime import datetime, timedelta

MAX_INTENTOS = 3
ESPERAS = (timedelta(minutes=1), timedelta(minutes=2))


@dataclass(frozen=True)
class IntentoGeneracion:
    id_acta: str
    numero: int
    fecha: datetime
    resultado: str

    @staticmethod
    def espera_tras(numero: int) -> timedelta:
        """Regla de ADR-001: espera creciente de 1 min tras el intento 1 y de 2 min tras el intento 2."""
        return ESPERAS[numero - 1]
