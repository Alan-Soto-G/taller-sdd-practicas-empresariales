"""Error: la Empresa no existe (CU-02, ADR-007)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class EmpresaNoEncontrada(ErrorAplicacion):
    def __init__(self, id_empresa: str) -> None:
        self.id_empresa = id_empresa
        super().__init__("empresa_no_encontrada", "empresa no encontrada")