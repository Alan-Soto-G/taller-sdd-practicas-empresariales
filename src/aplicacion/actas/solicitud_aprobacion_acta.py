"""DTO de entrada de AprobarActa para el Tutor o el Coordinador, autenticados con su token (CU-08)."""

from dataclasses import dataclass

from aplicacion.usuario_autenticado import UsuarioAutenticado


@dataclass(frozen=True)
class SolicitudAprobacionActa:
    usuario: UsuarioAutenticado
    id_acta: str
