"""ReglaPractica: version del reglamento como dato, no codigo: horas requeridas, carga maxima por tutor, plantilla del acta y criterios de evaluacion (vista logica, ADR-008)."""

from dataclasses import dataclass

from dominio.criterio_evaluacion import CriterioEvaluacion


@dataclass(frozen=True)
class ReglaPractica:
    version: str
    horas_requeridas: int
    carga_maxima_tutor: int
    plantilla_acta: str
    criterios: tuple[CriterioEvaluacion, ...] = ()
