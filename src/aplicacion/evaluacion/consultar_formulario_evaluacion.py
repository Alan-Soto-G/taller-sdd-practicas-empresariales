"""Caso de uso CU-06 (paso 2): el Representante abre el enlace y recibe el formulario con los criterios de la ReglaPractica de la Practica (ADR-005, ADR-008)."""

from aplicacion.configuracion.consultar_criterios_evaluacion import ConsultarCriteriosEvaluacion
from aplicacion.errores.practica_no_encontrada import PracticaNoEncontrada
from aplicacion.evaluacion.formulario_evaluacion import FormularioEvaluacion
from aplicacion.identidad_enlace import IdentidadEnlace
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas


class ConsultarFormularioEvaluacion:
    """Arma el formulario de evaluacion; abrirlo no consume el enlace."""

    def __init__(
        self,
        repositorio: RepositorioPracticas,
        consultar_criterios: ConsultarCriteriosEvaluacion,
    ) -> None:
        self._repositorio = repositorio
        self._consultar_criterios = consultar_criterios

    def ejecutar(self, identidad: IdentidadEnlace) -> FormularioEvaluacion:
        """Devuelve los criterios de la version de reglas con la que empezo la Practica."""
        practica = self._repositorio.obtener_practica(identidad.id_practica)
        if practica is None:
            raise PracticaNoEncontrada(identidad.id_practica)
        return FormularioEvaluacion(
            practica.id,
            practica.id_estudiante,
            self._consultar_criterios.ejecutar(practica.version_regla),
        )
