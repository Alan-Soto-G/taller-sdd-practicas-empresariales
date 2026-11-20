"""Plaza: vacante de practica que ofrece una Empresa (vista logica, CU-01, CU-02)."""

import re
from dataclasses import dataclass

FORMATO_PERIODO = re.compile(r"\d{4}-[12]")


@dataclass(frozen=True)
class Plaza:
    id: str
    id_empresa: str
    cargo: str
    cupos: int
    periodo: str

    def tiene_cupo(self, aceptadas: int) -> bool:
        """Regla: no admite mas postulaciones aceptadas que cupos."""
        return aceptadas < self.cupos

    @staticmethod
    def motivo_invalidez(cargo: str, cupos: int, periodo: str) -> str | None:
        """Regla de CU-02: devuelve el motivo por el que los datos no son validos, o None si lo son."""
        if not cargo or not cargo.strip():
            return "el cargo es obligatorio"
        if cupos <= 0:
            return "los cupos deben ser mayores que cero"
        if not FORMATO_PERIODO.fullmatch(periodo):
            return "el periodo debe tener el formato AAAA-1 o AAAA-2"
        return None
