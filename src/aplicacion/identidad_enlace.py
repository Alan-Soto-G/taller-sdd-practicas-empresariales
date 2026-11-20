"""DTO: identidad acotada a una practica y a una accion que entrega el Validador de enlace al Representante de la Empresa (ADR-005)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class IdentidadEnlace:
    id_enlace: str
    id_practica: str
    id_representante: str
    accion: str
