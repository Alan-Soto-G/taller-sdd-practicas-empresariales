"""Adaptador de entrada: valida el token de corta vida del usuario institucional y entrega su identidad y rol (ADR-004)."""

from aplicacion.errores.no_autenticado import NoAutenticado
from aplicacion.puertos.proveedor_identidad import ProveedorIdentidad
from aplicacion.usuario_autenticado import UsuarioAutenticado


class ValidadorToken:
    """Valida tokens mediante el proveedor de identidad institucional."""

    def __init__(self, proveedor: ProveedorIdentidad) -> None:
        """Inicializa el validador con su proveedor."""
        self._proveedor = proveedor

    def validar(self, token: str | None) -> UsuarioAutenticado:
        """Valida el token y devuelve la identidad autenticada."""
        if token is None or token == "":
            raise NoAutenticado()
        return self._proveedor.validar(token)
