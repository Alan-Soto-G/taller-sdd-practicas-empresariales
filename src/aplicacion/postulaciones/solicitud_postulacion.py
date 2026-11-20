"""DTO de entrada del caso de uso PostularsePlaza (CU-01)."""

from dataclasses import dataclass

from aplicacion.usuario_autenticado import UsuarioAutenticado


@dataclass(frozen=True)
class SolicitudPostulacion:
    usuario: UsuarioAutenticado
    id_plaza: str
