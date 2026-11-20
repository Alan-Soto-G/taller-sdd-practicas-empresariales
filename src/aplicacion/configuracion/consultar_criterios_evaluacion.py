"""Caso de uso del Modulo Configuracion: criterios de evaluacion de una version de ReglaPractica (ADR-008). Lo usa el Modulo Evaluacion (CU-06)."""

from aplicacion.configuracion.criterio_consultado import CriterioConsultado
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas


class ConsultarCriteriosEvaluacion:
    """Entrega los criterios de la version de reglas con la que empezo una Practica."""

    def __init__(self, repositorio: RepositorioPracticas) -> None:
        self._repositorio = repositorio

    def ejecutar(self, version: str) -> tuple[CriterioConsultado, ...]:
        """Devuelve los criterios de la ReglaPractica de esa version, en su orden."""
        regla = self._repositorio.obtener_regla(version)
        if regla is None:
            raise ValueError(f"no existe la ReglaPractica {version}")
        return tuple(
            CriterioConsultado(criterio.nombre, criterio.escala)
            for criterio in regla.criterios
        )
