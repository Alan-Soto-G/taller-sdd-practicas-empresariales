"""Error: el Repositorio de actas no pudo guardar o leer el PDF; lo traduce su adaptador (ADR-003, ADR-007)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class AlmacenNoDisponible(ErrorAplicacion):
    def __init__(self) -> None:
        super().__init__("almacen_no_disponible", "repositorio de actas no disponible")
