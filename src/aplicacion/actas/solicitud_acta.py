"""Mensaje SolicitudActa: lo publica la API en la cola actas y lo consume el Worker de actas (glosario, ADR-001)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SolicitudActa:
    id_acta: str
    id_practica: str
    intento: int
