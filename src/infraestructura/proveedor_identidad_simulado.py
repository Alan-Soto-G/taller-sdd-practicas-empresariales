"""Adaptador SSO simulado que implementa ProveedorIdentidad mientras TI habilita la integracion (ADR-004, R-03). Tokens de corta vida: 15 minutos."""

from collections.abc import Callable
from datetime import datetime, timedelta

from aplicacion.errores.no_autenticado import NoAutenticado
from aplicacion.usuario_autenticado import UsuarioAutenticado

VIDA_TOKEN = timedelta(minutes=15)


class ProveedorIdentidadSimulado:
    """Proveedor de identidad simulado en memoria."""

    def __init__(self, reloj: Callable[[], datetime] = datetime.now) -> None:
        """Inicializa el almacén de tokens y el reloj del sistema."""
        self._reloj = reloj
        self._tokens: dict[str, tuple[UsuarioAutenticado, datetime]] = {}

    def emitir(self, token: str, id_usuario: str, rol: str, emitido_en: datetime) -> None:
        """Registra un token simulando la emisión por parte del SSO."""
        self._tokens[token] = (UsuarioAutenticado(id_usuario, rol), emitido_en)

    def validar(self, token: str) -> UsuarioAutenticado:
        """Valida un token existente y no expirado, devolviendo el usuario autenticado."""
        if token not in self._tokens:
            raise NoAutenticado()

        usuario, emitido_en = self._tokens[token]
        if self._reloj() - emitido_en > VIDA_TOKEN:
            raise NoAutenticado()

        return usuario
