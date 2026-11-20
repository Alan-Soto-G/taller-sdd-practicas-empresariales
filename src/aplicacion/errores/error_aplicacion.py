"""Base del catalogo de errores de aplicacion (ADR-007)."""


class ErrorAplicacion(Exception):
    """Error de aplicacion con codigo estable y mensaje para el usuario."""

    def __init__(self, codigo: str, mensaje: str) -> None:
        self.codigo = codigo
        self.mensaje = mensaje
        super().__init__(mensaje)
