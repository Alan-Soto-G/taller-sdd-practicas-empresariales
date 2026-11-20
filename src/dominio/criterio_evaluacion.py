"""CriterioEvaluacion: aspecto que la empresa califica de 1 a la escala; es un dato de la ReglaPractica (vista logica, ADR-008)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CriterioEvaluacion:
    nombre: str
    escala: int
