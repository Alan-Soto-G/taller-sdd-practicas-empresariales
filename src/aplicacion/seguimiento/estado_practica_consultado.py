"""DTO con el estado de una Practica, sus horas, su evaluacion y su acta, tal como lo ve el Estudiante (CU-10)."""

from dataclasses import dataclass

from aplicacion.actas.resumen_acta import ResumenActa
from dominio.estado_practica import EstadoPractica


@dataclass(frozen=True)
class EstadoPracticaConsultado:
    id_practica: str
    id_empresa: str
    id_tutor: str | None
    estado: EstadoPractica
    horas_aprobadas: int
    horas_requeridas: int
    horas_pendientes: int
    porcentaje: int
    evaluacion_registrada: bool
    acta: ResumenActa | None
