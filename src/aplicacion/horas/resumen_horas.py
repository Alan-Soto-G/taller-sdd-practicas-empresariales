"""DTO de salida de ResumirHorasPractica: horas aprobadas, requeridas y pendientes de una Practica (Modulo Horas, CU-09)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResumenHoras:
    horas_aprobadas: int
    horas_requeridas: int
    horas_pendientes: int
    porcentaje: int
