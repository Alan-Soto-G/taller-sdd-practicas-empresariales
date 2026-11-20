"""Evaluacion: evaluacion de desempeno registrada por la Empresa; califica todos los criterios de su ReglaPractica (vista logica, CU-06)."""

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Evaluacion:
    id: str
    id_practica: str
    calificaciones: dict[str, int]
    observaciones: str
    fecha: date

    @staticmethod
    def motivo_invalidez(escalas: dict[str, int], calificaciones: dict[str, int]) -> str | None:
        """Regla de CU-06: cada criterio se califica de 1 a su escala; devuelve el motivo o None si es valida."""
        for nombre in escalas:
            if nombre not in calificaciones:
                return f"falta calificar el criterio {nombre}"
        for nombre, escala in escalas.items():
            if not 1 <= calificaciones[nombre] <= escala:
                return f"la calificación de {nombre} debe estar entre 1 y {escala}"
        for nombre in calificaciones:
            if nombre not in escalas:
                return f"criterio desconocido: {nombre}"
        return None
