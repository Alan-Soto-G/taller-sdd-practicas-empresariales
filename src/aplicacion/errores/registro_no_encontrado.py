"""Error: el RegistroHoras no existe (CU-05, ADR-007)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class RegistroNoEncontrado(ErrorAplicacion):
    def __init__(self, id_registro: str) -> None:
        self.id_registro = id_registro
        super().__init__("registro_no_encontrado", "registro de horas no encontrado")
