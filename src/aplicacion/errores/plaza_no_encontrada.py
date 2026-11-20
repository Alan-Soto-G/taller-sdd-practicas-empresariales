"""Error: la Plaza no existe (ADR-007)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class PlazaNoEncontrada(ErrorAplicacion):
    def __init__(self, id_plaza: str) -> None:
        self.id_plaza = id_plaza
        super().__init__("plaza_no_encontrada", "plaza no encontrada")
