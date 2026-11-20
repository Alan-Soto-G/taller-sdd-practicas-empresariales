"""DTO de salida de ConsultarAvanceTutor (CU-09)."""

from dataclasses import dataclass

from aplicacion.seguimiento.avance_practica import AvancePractica


@dataclass(frozen=True)
class AvanceTutor:
    id_tutor: str
    practicas: tuple[AvancePractica, ...]
