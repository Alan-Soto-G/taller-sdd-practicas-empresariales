"""DTO de entrada de ImportarHistorico: el libro de Excel ya leido, por hoja, como filas por encabezado (CU-13)."""

from dataclasses import dataclass

from aplicacion.usuario_autenticado import UsuarioAutenticado


@dataclass(frozen=True)
class SolicitudImportacion:
    usuario: UsuarioAutenticado
    hojas: dict[str, list[dict[str, str]]]
