"""Error: la Postulacion viola una regla del negocio de CU-01 (ADR-007)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class PostulacionNoPermitida(ErrorAplicacion):
    """Motivos: sin cupos, con una aceptada en el periodo o ya postulado a la plaza."""

    def __init__(self, motivo: str) -> None:
        self.motivo = motivo
        super().__init__("postulacion_no_permitida", "postulación no permitida")
