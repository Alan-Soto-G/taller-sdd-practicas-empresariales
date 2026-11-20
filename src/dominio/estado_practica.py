"""Estados de una Practica (vista logica, ciclo de vida; CU-03)."""
from enum import StrEnum


class EstadoPractica(StrEnum):
    SIN_TUTOR = 'sin tutor'
    EN_CURSO = 'en curso'
    HORAS_COMPLETAS = 'horas completas'
    EVALUADA = 'evaluada'
    ACTA_EN_TRAMITE = 'acta en trámite'
    CERRADA = 'cerrada'
