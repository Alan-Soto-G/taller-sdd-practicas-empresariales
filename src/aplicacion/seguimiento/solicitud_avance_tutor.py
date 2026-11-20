"""DTO de entrada de ConsultarAvanceTutor: todas las practicas del Tutor o una sola (CU-09)."""

from dataclasses import dataclass

from aplicacion.usuario_autenticado import UsuarioAutenticado


@dataclass(frozen=True)
class SolicitudAvanceTutor:
    usuario: UsuarioAutenticado
    id_practica: str | None = None
