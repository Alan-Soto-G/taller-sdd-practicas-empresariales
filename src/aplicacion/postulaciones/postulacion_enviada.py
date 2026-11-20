"""DTO de salida del caso de uso PostularsePlaza (CU-01)."""

from dataclasses import dataclass
from datetime import date

from dominio.estado_postulacion import EstadoPostulacion


@dataclass(frozen=True)
class PostulacionEnviada:
    id: str
    id_plaza: str
    estado: EstadoPostulacion
    fecha: date
