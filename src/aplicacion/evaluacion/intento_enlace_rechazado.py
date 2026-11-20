"""DTO de entrada de RegistrarEnlaceRechazado: el intento con un enlace vencido, usado o invalido (ADR-005, ADR-006)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class IntentoEnlaceRechazado:
    id_enlace: str | None
    id_representante: str | None
    motivo: str
