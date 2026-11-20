"""Puerto para guardar y leer los PDF de las actas (glosario: AlmacenActas; ADR-003). Lo implementa infraestructura."""

from typing import Protocol


class AlmacenActas(Protocol):
    def guardar(self, id_acta: str, contenido: bytes) -> str:
        """Guarda el PDF del acta y devuelve su ruta; lanza AlmacenNoDisponible si falla."""
        ...

    def leer(self, ruta: str) -> bytes:
        """Devuelve el PDF guardado en la ruta; lanza AlmacenNoDisponible si falla."""
        ...
