"""DTO: identidad y rol del usuario que entrega el Validador de token (ADR-004)."""
from dataclasses import dataclass


@dataclass(frozen=True)
class UsuarioAutenticado:
    id: str
    rol: str
