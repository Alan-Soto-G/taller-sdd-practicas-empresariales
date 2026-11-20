"""DTO de salida de ConsultarReglaVigente (Modulo Configuracion, ADR-008)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ReglaVigente:
    version: str
    horas_requeridas: int
    carga_maxima_tutor: int
    plantilla_acta: str
