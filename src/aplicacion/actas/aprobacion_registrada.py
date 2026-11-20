"""DTO de salida de AprobarActa: cuantas aprobaciones lleva el acta y el estado del acta y de la Practica (CU-08)."""

from dataclasses import dataclass

from dominio.estado_acta import EstadoActa
from dominio.estado_practica import EstadoPractica


@dataclass(frozen=True)
class AprobacionRegistrada:
    id_acta: str
    rol: str
    aprobaciones: int
    estado_acta: EstadoActa
    estado_practica: EstadoPractica
