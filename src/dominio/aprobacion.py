"""Aprobacion: aprobacion electronica del acta por tutor, empresa o coordinador; reemplaza la firma manual (vista logica, ADR-006)."""

from dataclasses import dataclass
from datetime import datetime

APROBACIONES_REQUERIDAS = 3


@dataclass(frozen=True)
class Aprobacion:
    id_acta: str
    rol: str
    usuario: str
    fecha: datetime
