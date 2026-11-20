"""Puerto para validar la identidad contra el Directorio Activo / SSO (glosario: ProveedorIdentidad; ADR-004). Lo implementa infraestructura."""

from typing import Protocol

from aplicacion.usuario_autenticado import UsuarioAutenticado


class ProveedorIdentidad(Protocol):
    def validar(self, token: str) -> UsuarioAutenticado:
        """Devuelve el usuario del token; lanza NoAutenticado si es invalido o vencio."""
        ...
