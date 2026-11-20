"""Puerto que lee las hojas de un archivo .xlsx como filas por encabezado (glosario: LectorExcel; ADR-012). Lo implementa infraestructura."""

from typing import Protocol


class LectorExcel(Protocol):
    def leer(self, contenido: bytes) -> dict[str, list[dict[str, str]]]:
        """Devuelve, por hoja, sus filas como textos por encabezado (la fila 1 es el encabezado); lanza ArchivoNoValido."""
        ...
