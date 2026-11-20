"""DTO de salida de GenerarReporte: conteos de practicas, actas y horas (CU-11)."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class ReportePracticas:
    id_empresa: str | None
    total_practicas: int
    por_estado: dict[str, int]
    por_empresa: dict[str, int]
    por_tutor: dict[str, int]
    actas_por_estado: dict[str, int]
    horas_aprobadas: int
    generado: datetime
