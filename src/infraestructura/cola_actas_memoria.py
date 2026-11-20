"""Adaptador en memoria del Broker de mensajes (sustituye a RabbitMQ en esta etapa; ADR-001): cola actas y cola errores_actas. Implementa PublicadorActas."""

from collections.abc import Callable
from datetime import datetime
from threading import Lock

from aplicacion.actas.solicitud_acta import SolicitudActa


class ColaActasMemoria:
    """Guarda las SolicitudActa hasta que el Worker de actas las procese; ninguna se pierde."""

    def __init__(self, reloj: Callable[[], datetime] = datetime.now) -> None:
        self._reloj = reloj
        self._actas: list[tuple[datetime, SolicitudActa]] = []
        self._errores: list[SolicitudActa] = []
        self._candado = Lock()

    def publicar(self, solicitud: SolicitudActa) -> None:
        """Deja la solicitud en la cola actas, disponible desde ya."""
        self.reencolar(solicitud, self._reloj())

    def reencolar(self, solicitud: SolicitudActa, disponible_desde: datetime) -> None:
        """Deja la solicitud en la cola actas, disponible desde la hora indicada (espera creciente)."""
        with self._candado:
            self._actas.append((disponible_desde, solicitud))

    def tomar(self, ahora: datetime) -> SolicitudActa | None:
        """Saca la primera solicitud disponible a esa hora, o None si no hay."""
        with self._candado:
            for indice, (disponible_desde, solicitud) in enumerate(self._actas):
                if disponible_desde <= ahora:
                    del self._actas[indice]
                    return solicitud
            return None

    def enviar_a_errores(self, solicitud: SolicitudActa) -> None:
        """Deja la solicitud en la cola errores_actas para el Coordinador (DT-01)."""
        with self._candado:
            self._errores.append(solicitud)

    def listar_actas(self) -> list[tuple[datetime, SolicitudActa]]:
        """Devuelve una copia de la cola actas con la hora desde la que cada solicitud esta disponible."""
        with self._candado:
            return list(self._actas)

    def listar_errores(self) -> list[SolicitudActa]:
        """Devuelve una copia de la cola errores_actas."""
        with self._candado:
            return list(self._errores)
