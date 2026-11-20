"""Error: la operacion sobre la Empresa entra en conflicto con los datos existentes (CU-14, ADR-007)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class EmpresaNoPermitida(ErrorAplicacion):
    """Motivos: el id ya existe o la empresa tiene plazas o practicas."""

    def __init__(self, motivo: str) -> None:
        self.motivo = motivo
        super().__init__("empresa_no_permitida", "empresa no permitida")
