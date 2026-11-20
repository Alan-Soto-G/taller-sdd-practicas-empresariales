"""Error: la Practica no admite la evaluacion en su estado actual (CU-06, ADR-007)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class EvaluacionNoPermitida(ErrorAplicacion):
    """Motivos: la practica no tiene las horas completas, no esta lista para evaluar o la empresa no tiene representante."""

    def __init__(self, motivo: str) -> None:
        self.motivo = motivo
        super().__init__("evaluacion_no_permitida", "evaluación no permitida")
