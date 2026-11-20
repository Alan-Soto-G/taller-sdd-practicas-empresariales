"""EnlaceAcceso: enlace de un solo uso y con vencimiento para el Representante de la Empresa (vista logica, ADR-005)."""

from dataclasses import dataclass, replace
from datetime import datetime, timedelta

VIGENCIA_ENLACE = timedelta(days=7)


@dataclass(frozen=True)
class EnlaceAcceso:
    id: str
    token: str
    id_practica: str
    id_representante: str
    accion: str
    vence: datetime
    usado: bool = False

    @classmethod
    def emitir(cls, id: str, token: str, id_practica: str, id_representante: str, accion: str, ahora: datetime) -> "EnlaceAcceso":
        """Crea un enlace sin usar que vence a los 7 dias (ADR-005)."""
        return cls(id, token, id_practica, id_representante, accion, ahora + VIGENCIA_ENLACE)

    def motivo_rechazo(self, accion: str, ahora: datetime) -> str | None:
        """Regla de ADR-005: devuelve por que el enlace no sirve para la accion, o None si es valido."""
        if accion != self.accion:
            return "enlace inválido"
        if self.usado:
            return "enlace usado"
        if ahora > self.vence:
            return "enlace vencido"
        return None

    def usar(self) -> "EnlaceAcceso":
        """Invalida el enlace al usarlo o al reemitirlo (un solo uso)."""
        if self.usado:
            raise ValueError("enlace usado")
        return replace(self, usado=True)
