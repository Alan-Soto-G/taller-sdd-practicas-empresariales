"""Puerto para registrar la auditoria (glosario: Bitacora; ADR-006). Lo implementa infraestructura."""

from datetime import datetime
from typing import Protocol


class Bitacora(Protocol):
    def registrar(self, usuario: str, rol: str, recurso: str, accion: str, hora: datetime) -> None:
        """Registra un cambio de estado o un acceso rechazado."""
        ...
