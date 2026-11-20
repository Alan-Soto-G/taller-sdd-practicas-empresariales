"""Error: los datos de la Empresa o de su representante no son validos (CU-14, ADR-007)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class EmpresaNoValida(ErrorAplicacion):
    """Motivos: razon social, NIT, nombre del representante o correo."""

    def __init__(self, motivo: str) -> None:
        self.motivo = motivo
        super().__init__("empresa_no_valida", "empresa no válida")
