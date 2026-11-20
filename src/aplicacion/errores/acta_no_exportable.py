"""Error: el ActaFinal todavia no tiene un PDF que exportar (CU-12, ADR-007)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class ActaNoExportable(ErrorAplicacion):
    """Motivo: el acta no tiene PDF generado (en generacion o con error)."""

    def __init__(self, motivo: str) -> None:
        self.motivo = motivo
        super().__init__("acta_no_exportable", "exportación no permitida")
