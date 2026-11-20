"""DTO de entrada del caso de uso AprobarHoras: decision 'aprobar' o 'rechazar' (CU-05)."""

from dataclasses import dataclass

from aplicacion.usuario_autenticado import UsuarioAutenticado


@dataclass(frozen=True)
class SolicitudRevisionHoras:
    usuario: UsuarioAutenticado
    id_registro: str
    decision: str
