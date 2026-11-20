"""Caso de uso del Modulo Actas (solo lectura): resume el acta mas reciente de una Practica para el Modulo Seguimiento (CU-10, ADR-002)."""

from aplicacion.actas.resumen_acta import ResumenActa
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas


class ConsultarActaPractica:
    """Devuelve el estado del acta de la Practica y sus aprobaciones, o None si aun no se solicito."""

    def __init__(self, repositorio: RepositorioPracticas) -> None:
        self._repositorio = repositorio

    def ejecutar(self, id_practica: str) -> ResumenActa | None:
        """Resume el acta mas reciente de la Practica."""
        acta = self._repositorio.obtener_acta_de_practica(id_practica)
        if acta is None:
            return None
        aprobaciones = len(self._repositorio.listar_aprobaciones(acta.id))
        return ResumenActa(acta.id, acta.estado, aprobaciones)
