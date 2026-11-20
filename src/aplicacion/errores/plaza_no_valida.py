"""Error: los datos de la Plaza no son validos en CU-02 (ADR-007)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class PlazaNoValida(ErrorAplicacion):
    """Motivos: cargo vacio, cupos no mayores que cero o periodo con formato distinto de AAAA-1 o AAAA-2."""

    def __init__(self, motivo: str) -> None:
        self.motivo = motivo
        super().__init__("plaza_no_valida", "plaza no válida")
