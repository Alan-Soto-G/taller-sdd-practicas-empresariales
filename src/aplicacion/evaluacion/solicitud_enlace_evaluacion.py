"""DTO de entrada del caso de uso EmitirEnlaceEvaluacion (CU-06)."""

from dataclasses import dataclass

from aplicacion.usuario_autenticado import UsuarioAutenticado


@dataclass(frozen=True)
class SolicitudEnlaceEvaluacion:
    usuario: UsuarioAutenticado
    id_practica: str
