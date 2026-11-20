"""Adaptador en memoria de Bitacora (sustituye al Adaptador de bitacora sobre PostgreSQL en esta etapa; ADR-006)."""

from datetime import datetime


class BitacoraMemoria:
    """Registra eventos de bitacora en memoria."""

    def __init__(self) -> None:
        """Inicializa la lista de registros."""
        self._registros: list[dict[str, object]] = []

    def registrar(
        self,
        usuario: str,
        rol: str,
        recurso: str,
        accion: str,
        hora: datetime,
    ) -> None:
        """Agrega un registro a la bitacora."""
        self._registros.append(
            {
                "usuario": usuario,
                "rol": rol,
                "recurso": recurso,
                "accion": accion,
                "hora": hora,
            }
        )

    def listar(self) -> list[dict[str, object]]:
        """Devuelve una copia de los registros."""
        return list(self._registros)
