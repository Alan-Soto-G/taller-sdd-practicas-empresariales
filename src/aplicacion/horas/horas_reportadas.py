"""DTO de salida del caso de uso RegistrarHoras (CU-04)."""

from dataclasses import dataclass
from datetime import date

from dominio.estado_registro_horas import EstadoRegistroHoras


@dataclass(frozen=True)
class HorasReportadas:
    id: str
    id_practica: str
    semana: str
    horas: int
    estado: EstadoRegistroHoras
    fecha: date
