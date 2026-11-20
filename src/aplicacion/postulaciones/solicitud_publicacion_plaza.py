"""DTO de entrada del caso de uso PublicarPlaza (CU-02)."""

from dataclasses import dataclass

from aplicacion.usuario_autenticado import UsuarioAutenticado


@dataclass(frozen=True)
class SolicitudPublicacionPlaza:
    usuario: UsuarioAutenticado
    id_empresa: str
    cargo: str
    cupos: int
    periodo: str
