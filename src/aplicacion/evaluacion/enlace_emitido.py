"""DTO de salida del caso de uso EmitirEnlaceEvaluacion; no incluye el token, que solo viaja por correo (CU-06, ADR-005)."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class EnlaceEmitido:
    id_enlace: str
    id_practica: str
    vence: datetime
    correo_representante: str
