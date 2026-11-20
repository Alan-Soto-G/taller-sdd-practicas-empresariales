"""Estados de un ActaFinal (vista logica, CU-07)."""

from enum import StrEnum


class EstadoActa(StrEnum):
    EN_GENERACION = "en generación"
    GENERADA = "generada"
    APROBADA = "aprobada"
    CON_ERROR = "con error"
