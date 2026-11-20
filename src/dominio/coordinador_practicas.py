"""CoordinadorPracticas: gestiona plazas, empresas, asignaciones y actas (glosario, CU-07)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CoordinadorPracticas:
    id: str
    correo: str
