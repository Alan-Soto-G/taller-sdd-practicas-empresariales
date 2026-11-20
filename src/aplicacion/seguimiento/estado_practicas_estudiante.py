"""DTO de salida de ConsultarEstadoPractica (CU-10)."""

from dataclasses import dataclass

from aplicacion.seguimiento.estado_practica_consultado import EstadoPracticaConsultado


@dataclass(frozen=True)
class EstadoPracticasEstudiante:
    id_estudiante: str
    practicas: tuple[EstadoPracticaConsultado, ...]
