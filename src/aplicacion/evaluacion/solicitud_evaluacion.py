"""DTO de entrada del caso de uso RegistrarEvaluacion (CU-06)."""

from dataclasses import dataclass

from aplicacion.identidad_enlace import IdentidadEnlace


@dataclass(frozen=True)
class SolicitudEvaluacion:
    identidad: IdentidadEnlace
    calificaciones: dict[str, int]
    observaciones: str
