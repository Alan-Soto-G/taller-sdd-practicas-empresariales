"""Error: el EnlaceAcceso esta vencido, usado o es invalido (ADR-005, ADR-007)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class EnlaceNoValido(ErrorAplicacion):
    """Motivos: enlace vencido, enlace usado o enlace inválido."""

    def __init__(self, motivo: str) -> None:
        self.motivo = motivo
        super().__init__(
            "enlace_no_valido",
            "enlace vencido: solicite uno nuevo a la Coordinación",
        )
