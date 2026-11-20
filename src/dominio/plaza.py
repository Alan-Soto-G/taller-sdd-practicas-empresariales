"""Plaza: vacante de practica que ofrece una Empresa (vista logica, CU-01)."""

from dataclasses import dataclass


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
