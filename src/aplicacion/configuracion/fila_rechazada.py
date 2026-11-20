"""DTO con una fila del Excel que no se cargo y su motivo; la fila 1 es el encabezado (CU-13, ADR-008)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class FilaRechazada:
    hoja: str
    fila: int
    motivo: str
