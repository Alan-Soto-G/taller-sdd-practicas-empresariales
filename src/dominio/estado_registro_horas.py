"""Estados de un RegistroHoras (vista logica, CU-04)."""

from enum import StrEnum


class EstadoRegistroHoras(StrEnum):
    REPORTADO = 'reportado'
    APROBADO = 'aprobado'
    RECHAZADO = 'rechazado'
