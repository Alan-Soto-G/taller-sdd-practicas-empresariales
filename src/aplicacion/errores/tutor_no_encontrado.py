"""Error: el Tutor no existe (CU-03, ADR-007)."""

from aplicacion.errores.error_aplicacion import ErrorAplicacion


class TutorNoEncontrado(ErrorAplicacion):
    def __init__(self, id_tutor: str) -> None:
        self.id_tutor = id_tutor
        super().__init__("tutor_no_encontrado", "tutor no encontrado")
