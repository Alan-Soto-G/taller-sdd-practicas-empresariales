"""Caso de uso del Modulo Configuracion: consulta la ReglaPractica vigente (ADR-008). Lo usa el Modulo Asignacion (CU-03)."""

from aplicacion.configuracion.regla_vigente import ReglaVigente
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas


class ConsultarReglaVigente:
    """Entrega la version vigente de las reglas de la practica como dato."""

    def __init__(self, repositorio: RepositorioPracticas) -> None:
        self._repositorio = repositorio

    def ejecutar(self) -> ReglaVigente:
        """Devuelve la ReglaPractica vigente como DTO."""
        regla = self._repositorio.obtener_regla_vigente()
        return ReglaVigente(
            regla.version,
            regla.horas_requeridas,
            regla.carga_maxima_tutor,
            regla.plantilla_acta,
        )
