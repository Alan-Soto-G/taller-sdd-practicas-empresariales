"""DTO de entrada del caso de uso AsignarTutor (CU-03)."""

from dataclasses import dataclass

from aplicacion.usuario_autenticado import UsuarioAutenticado


@dataclass(frozen=True)
class SolicitudAsignacionTutor:
    usuario: UsuarioAutenticado
    id_tutor: str
    ids_practicas: tuple[str, ...]
