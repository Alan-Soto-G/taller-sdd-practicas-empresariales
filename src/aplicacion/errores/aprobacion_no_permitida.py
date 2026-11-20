"""Error: el ActaFinal no admite la aprobacion (CU-08, ADR-007)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class AprobacionNoPermitida(ErrorAplicacion):
    """Motivos: el acta no esta generada, el rol ya aprobo o la empresa no tiene representante."""

    def __init__(self, motivo: str) -> None:
        self.motivo = motivo
        super().__init__("aprobacion_no_permitida", "aprobación no permitida")
