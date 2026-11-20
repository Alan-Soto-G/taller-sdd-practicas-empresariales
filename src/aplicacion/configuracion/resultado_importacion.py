"""DTO de salida de ImportarHistorico: filas cargadas por hoja y filas rechazadas con su motivo (CU-13, ADR-008)."""

from dataclasses import dataclass

from aplicacion.configuracion.fila_rechazada import FilaRechazada


@dataclass(frozen=True)
class ResultadoImportacion:
    cargadas: dict[str, int]
    rechazadas: tuple[FilaRechazada, ...]
