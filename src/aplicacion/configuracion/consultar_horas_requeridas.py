"""Caso de uso del Modulo Configuracion: horas requeridas de una version de ReglaPractica (ADR-008). Lo usa el Modulo Horas (CU-05)."""

from aplicacion.puertos.repositorio_practicas import RepositorioPracticas


class ConsultarHorasRequeridas:
    """Entrega las horas requeridas de la version de reglas con la que empezo una Practica."""

    def __init__(self, repositorio: RepositorioPracticas) -> None:
        self._repositorio = repositorio

    def ejecutar(self, version: str) -> int:
        """Devuelve las horas requeridas de la ReglaPractica de esa version."""
        regla = self._repositorio.obtener_regla(version)
        if regla is None:
            raise ValueError(f"no existe la ReglaPractica {version}")
        return regla.horas_requeridas
