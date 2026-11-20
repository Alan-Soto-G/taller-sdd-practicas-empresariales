"""DTO con el resultado de asignar tutor a una Practica: 'asignada' o 'no asignada: <motivo>' (CU-03)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ResultadoPractica:
    id_practica: str
    resultado: str
