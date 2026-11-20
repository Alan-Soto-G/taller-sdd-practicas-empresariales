"""Adaptador en memoria del Repositorio de actas (sustituye al almacenamiento institucional en esta etapa; ADR-003). Implementa AlmacenActas."""

from aplicacion.errores.almacen_no_disponible import AlmacenNoDisponible


class AlmacenActasMemoria:
    """Guarda los PDF de las actas; puede simular fallas para los reintentos del Worker (ADR-001)."""

    def __init__(self) -> None:
        self.fallas_pendientes = 0
        self._archivos: dict[str, bytes] = {}

    def guardar(self, id_acta: str, contenido: bytes) -> str:
        """Guarda el PDF y devuelve su ruta; mientras haya fallas pendientes, falla y lo traduce a AlmacenNoDisponible (ADR-007)."""
        if self.fallas_pendientes > 0:
            self.fallas_pendientes -= 1
            raise AlmacenNoDisponible()
        ruta = f"actas/{id_acta}.pdf"
        self._archivos[ruta] = contenido
        return ruta

    def leer(self, ruta: str) -> bytes:
        """Devuelve el PDF guardado en la ruta; si no existe, AlmacenNoDisponible."""
        if ruta not in self._archivos:
            raise AlmacenNoDisponible()
        return self._archivos[ruta]

    def listar(self) -> list[str]:
        """Devuelve las rutas guardadas."""
        return list(self._archivos)
