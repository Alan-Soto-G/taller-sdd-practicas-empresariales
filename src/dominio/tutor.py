"""Tutor: docente que acompana la practica (vista logica, CU-03)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Tutor:
    id: str
    correo: str

    def tiene_cupo(self, carga_actual: int, carga_maxima: int) -> bool:
        """Regla: atiende como maximo la carga definida en ReglaPractica."""
        return carga_actual < carga_maxima
