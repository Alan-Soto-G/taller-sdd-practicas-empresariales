"""DTO de entrada del caso de uso SolicitarActas (CU-07)."""

from dataclasses import dataclass

from aplicacion.usuario_autenticado import UsuarioAutenticado


@dataclass(frozen=True)
class SolicitudGeneracionActas:
    usuario: UsuarioAutenticado
    ids_practicas: tuple[str, ...]
