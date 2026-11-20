"""DTO de salida de ConsultarFormularioEvaluacion: los criterios que el Representante califica (CU-06)."""

from dataclasses import dataclass

from aplicacion.configuracion.criterio_consultado import CriterioConsultado


@dataclass(frozen=True)
class FormularioEvaluacion:
    id_practica: str
    id_estudiante: str
    criterios: tuple[CriterioConsultado, ...]
