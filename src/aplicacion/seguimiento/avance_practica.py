"""DTO con el avance de horas de una Practica (CU-09)."""

from dataclasses import dataclass

from dominio.estado_practica import EstadoPractica


@dataclass(frozen=True)
class AvancePractica:
    id_practica: str
    id_estudiante: str
    estado: EstadoPractica
    horas_aprobadas: int
    horas_requeridas: int
    horas_pendientes: int
    porcentaje: int
