"""DTO de entrada de GenerarReporte: reporte general o filtrado por una Empresa (CU-11)."""

from dataclasses import dataclass

from aplicacion.usuario_autenticado import UsuarioAutenticado


@dataclass(frozen=True)
class SolicitudReporte:
    usuario: UsuarioAutenticado
    id_empresa: str | None = None
