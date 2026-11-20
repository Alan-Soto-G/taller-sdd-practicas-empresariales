"""DTO de entrada de ImportarHistorico cuando el Coordinador sube el archivo .xlsx (CU-13, ADR-012)."""

from dataclasses import dataclass

from aplicacion.usuario_autenticado import UsuarioAutenticado


@dataclass(frozen=True)
class SolicitudImportacionExcel:
    usuario: UsuarioAutenticado
    contenido: bytes
