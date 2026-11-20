"""DTO con los datos consolidados del acta que GenerarActa entrega al ComponedorActa (CU-07, ADR-011)."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class DatosActa:
    id_acta: str
    id_practica: str
    id_estudiante: str
    id_empresa: str
    id_tutor: str | None
    plantilla: str
    horas_aprobadas: int
    horas_requeridas: int
    calificaciones: dict[str, int]
    observaciones: str
    fecha_solicitud: datetime
