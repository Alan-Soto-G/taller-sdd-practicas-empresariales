"""Error: token ausente, invalido o vencido (ADR-004, ADR-007)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class NoAutenticado(ErrorAplicacion):
    def __init__(self) -> None:
        super().__init__("no_autenticado", "no autenticado")
