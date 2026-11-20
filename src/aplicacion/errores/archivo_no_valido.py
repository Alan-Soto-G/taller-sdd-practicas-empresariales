"""Error: el archivo subido no se puede leer como un Excel .xlsx; lo traduce el adaptador (CU-13, ADR-007, ADR-012)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class ArchivoNoValido(ErrorAplicacion):
    """Motivo: el archivo no es un Excel .xlsx valido."""

    def __init__(self, motivo: str) -> None:
        self.motivo = motivo
        super().__init__("archivo_no_valido", "archivo no válido")
