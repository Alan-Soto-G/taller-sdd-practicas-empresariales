"""Estados de una Postulacion (vista logica, CU-01)."""

from enum import StrEnum


class EstadoPostulacion(StrEnum):
    ENVIADA = 'enviada'
    ACEPTADA = 'aceptada'
    RECHAZADA = 'rechazada'