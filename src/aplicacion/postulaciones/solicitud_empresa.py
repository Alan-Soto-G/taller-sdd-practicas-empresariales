"""DTO de entrada de GestionarEmpresas para crear, actualizar o eliminar una Empresa (CU-14)."""

from dataclasses import dataclass

from aplicacion.usuario_autenticado import UsuarioAutenticado


@dataclass(frozen=True)
class SolicitudEmpresa:
    usuario: UsuarioAutenticado
    id_empresa: str
    razon_social: str = ""
    nit: str = ""
