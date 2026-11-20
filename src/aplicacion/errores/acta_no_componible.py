"""Error: el ComponedorActa no pudo componer el PDF del acta; lo traduce su adaptador (ADR-007, ADR-011)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class ActaNoComponible(ErrorAplicacion):
    def __init__(self) -> None:
        super().__init__("acta_no_componible", "no se pudo componer el PDF del acta")
