"""Postulacion: solicitud de un Estudiante a una Plaza (vista logica, CU-01)."""

from dataclasses import dataclass
from datetime import date

from dominio.estado_postulacion import EstadoPostulacion


@dataclass(frozen=True)
class Postulacion:
    id: str
    id_estudiante: str
    id_plaza: str
    periodo: str
    fecha: date
    estado: EstadoPostulacion

    @classmethod
    def enviar(
        cls, id: str, id_estudiante: str, id_plaza: str, periodo: str, fecha: date
    ) -> "Postulacion":
        """Crea una Postulacion nueva en estado enviada."""
        return cls(id, id_estudiante, id_plaza, periodo, fecha, EstadoPostulacion.ENVIADA)
