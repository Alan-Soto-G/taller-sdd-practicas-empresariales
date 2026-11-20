"""Error: las calificaciones de la Evaluacion no cumplen los criterios de su ReglaPractica (CU-06, ADR-007)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class EvaluacionNoValida(ErrorAplicacion):
    """Motivos: falta un criterio, criterio desconocido o calificacion fuera de la escala."""

    def __init__(self, motivo: str) -> None:
        self.motivo = motivo
        super().__init__("evaluacion_no_valida", "evaluación no válida")
