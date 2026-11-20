"""DTO de entrada de GestionarEmpresas para registrar o actualizar el representante de una Empresa (CU-14)."""

from dataclasses import dataclass

from aplicacion.usuario_autenticado import UsuarioAutenticado


@dataclass(frozen=True)
class SolicitudRepresentante:
    usuario: UsuarioAutenticado
    id_empresa: str
    nombre: str
    correo: str
