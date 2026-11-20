"""DTO de salida del Modulo Configuracion: un CriterioEvaluacion y su escala (ADR-008)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CriterioConsultado:
    nombre: str
    escala: int
