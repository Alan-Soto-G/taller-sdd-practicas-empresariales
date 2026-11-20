"""Error: el RegistroHoras viola una regla de CU-04 (ADR-007)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class RegistroNoValido(ErrorAplicacion):
    """Motivos: datos fuera de rango, semana con registro o practica que no esta en curso."""

    def __init__(self, motivo: str) -> None:
        self.motivo = motivo
        super().__init__("registro_no_valido", "registro no válido")
