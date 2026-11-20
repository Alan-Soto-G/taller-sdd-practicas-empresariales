"""Error: el ActaFinal no existe (CU-08, ADR-007)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class ActaNoEncontrada(ErrorAplicacion):
    def __init__(self, id_acta: str) -> None:
        self.id_acta = id_acta
        super().__init__("acta_no_encontrada", "acta no encontrada")
