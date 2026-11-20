"""DTO de salida del caso de uso AprobarHoras (CU-05)."""

from dataclasses import dataclass

from dominio.estado_practica import EstadoPractica
from dominio.estado_registro_horas import EstadoRegistroHoras


@dataclass(frozen=True)
class HorasRevisadas:
    id: str
    id_practica: str
    estado: EstadoRegistroHoras
    horas_aprobadas: int
    estado_practica: EstadoPractica
