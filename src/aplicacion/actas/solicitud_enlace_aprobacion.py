"""DTO de entrada del caso de uso EmitirEnlaceAprobacion (CU-08)."""

from dataclasses import dataclass

from aplicacion.usuario_autenticado import UsuarioAutenticado


@dataclass(frozen=True)
class SolicitudEnlaceAprobacion:
    usuario: UsuarioAutenticado
    id_acta: str
