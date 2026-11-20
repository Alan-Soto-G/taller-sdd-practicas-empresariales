"""Puerto que compone el PDF del acta a partir de sus datos consolidados (glosario: ComponedorActa; ADR-011). Lo implementa infraestructura; solo lo usa el Worker de actas (ADR-001)."""

from typing import Protocol

from aplicacion.actas.datos_acta import DatosActa


class ComponedorActa(Protocol):
    def componer(self, datos: DatosActa) -> bytes:
        """Devuelve el PDF del acta; lanza ActaNoComponible si falla."""
        ...
