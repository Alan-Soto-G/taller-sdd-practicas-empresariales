"""DTO de salida de ExportarActa: el PDF del acta listo para descargar (CU-12)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ActaExportada:
    id_acta: str
    nombre_archivo: str
    tipo_contenido: str
    contenido: bytes
