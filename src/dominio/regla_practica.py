"""ReglaPractica: version del reglamento como dato, no codigo (vista logica, ADR-008)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ReglaPractica:
    version: str
    horas_requeridas: int
    carga_maxima_tutor: int
    plantilla_acta: str
