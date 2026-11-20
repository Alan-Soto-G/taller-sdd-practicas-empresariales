"""DTO de entrada de ConsultarEstadoPractica: todas las practicas del Estudiante o una sola (CU-10)."""

from dataclasses import dataclass

from aplicacion.usuario_autenticado import UsuarioAutenticado


@dataclass(frozen=True)
class SolicitudEstadoPractica:
    usuario: UsuarioAutenticado
    id_practica: str | None = None
