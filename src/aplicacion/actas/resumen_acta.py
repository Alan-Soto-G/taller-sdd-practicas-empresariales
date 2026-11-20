"""DTO de salida de ConsultarActaPractica: estado del acta y cuantas aprobaciones tiene (Modulo Actas, CU-10)."""

from dataclasses import dataclass

from dominio.estado_acta import EstadoActa


@dataclass(frozen=True)
class ResumenActa:
    id_acta: str
    estado: EstadoActa
    aprobaciones: int
