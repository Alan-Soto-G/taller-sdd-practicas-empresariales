"""DTO de entrada del caso de uso ExportarActa (CU-12)."""

from dataclasses import dataclass

from aplicacion.usuario_autenticado import UsuarioAutenticado


@dataclass(frozen=True)
class SolicitudExportacionActa:
    usuario: UsuarioAutenticado
    id_acta: str
