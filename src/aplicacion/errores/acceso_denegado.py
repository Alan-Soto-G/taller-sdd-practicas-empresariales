"""Error: el usuario no tiene el rol o la titularidad requeridos (ADR-004, ADR-007)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class AccesoDenegado(ErrorAplicacion):
    def __init__(self) -> None:
        super().__init__("acceso_denegado", "acceso denegado")
