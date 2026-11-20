"""DTO de entrada del caso de uso RegistrarHoras (CU-04)."""

from dataclasses import dataclass

from aplicacion.usuario_autenticado import UsuarioAutenticado


@dataclass(frozen=True)
class SolicitudRegistroHoras:
    usuario: UsuarioAutenticado
    id_practica: str
    semana: str
    horas: int
    actividades: str
