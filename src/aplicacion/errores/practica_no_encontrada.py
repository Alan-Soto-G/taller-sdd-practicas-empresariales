"""Error: la Practica no existe (CU-04, ADR-007)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class PracticaNoEncontrada(ErrorAplicacion):
    def __init__(self, id_practica: str) -> None:
        self.id_practica = id_practica
        super().__init__("practica_no_encontrada", "práctica no encontrada")
