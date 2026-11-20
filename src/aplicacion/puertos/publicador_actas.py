"""Puerto que publica las solicitudes de acta en la cola actas (glosario: PublicadorActas; ADR-001). Lo implementa infraestructura."""

from typing import Protocol

from aplicacion.actas.solicitud_acta import SolicitudActa


class PublicadorActas(Protocol):
    def publicar(self, solicitud: SolicitudActa) -> None:
        """Deja la SolicitudActa en la cola actas para el Worker de actas."""
        ...
