"""RegistroHoras: horas reportadas por el Estudiante en una semana (vista logica, CU-04)."""

import re
from dataclasses import dataclass
from datetime import date

from dominio.estado_registro_horas import EstadoRegistroHoras

FORMATO_SEMANA = re.compile(r"\d{4}-W(0[1-9]|[1-4]\d|5[0-3])")
HORAS_MINIMAS = 1
HORAS_MAXIMAS = 168


@dataclass(frozen=True)
class RegistroHoras:
    id: str
    id_practica: str
    semana: str
    horas: int
    actividades: str
    fecha: date
    estado: EstadoRegistroHoras

    @classmethod
    def reportar(
        cls,
        id: str,
        id_practica: str,
        semana: str,
        horas: int,
        actividades: str,
        fecha: date,
    ) -> "RegistroHoras":
        """Crea un RegistroHoras nuevo en estado reportado."""
        return cls(
            id,
            id_practica,
            semana,
            horas,
            actividades,
            fecha,
            EstadoRegistroHoras.REPORTADO,
        )

    @staticmethod
    def motivo_invalidez(semana: str, horas: int, actividades: str) -> str | None:
        """Regla de CU-04: devuelve el motivo por el que los datos no son validos, o None si lo son."""
        if not FORMATO_SEMANA.fullmatch(semana):
            return "la semana debe tener el formato AAAA-Wss (semana 01 a 53)"
        if horas < HORAS_MINIMAS or horas > HORAS_MAXIMAS:
            return "las horas deben estar entre 1 y 168"
        if not actividades or not actividades.strip():
            return "las actividades son obligatorias"
        return None
