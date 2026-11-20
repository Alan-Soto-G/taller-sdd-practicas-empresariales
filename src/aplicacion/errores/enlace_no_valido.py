"""Error: el EnlaceAcceso esta vencido, usado o es invalido; lleva el enlace y el representante para que un caso de uso audite el intento (ADR-005, ADR-006, ADR-007)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class EnlaceNoValido(ErrorAplicacion):
    """Motivos: enlace vencido, enlace usado o enlace inválido."""

    def __init__(
        self,
        motivo: str,
        id_enlace: str | None = None,
        id_representante: str | None = None,
    ) -> None:
        self.motivo = motivo
        self.id_enlace = id_enlace
        self.id_representante = id_representante
        super().__init__(
            "enlace_no_valido",
            "enlace vencido: solicite uno nuevo a la Coordinación",
        )
