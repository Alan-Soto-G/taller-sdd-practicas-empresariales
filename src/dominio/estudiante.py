"""Estudiante: quien realiza la practica (vista logica, CU-03)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Estudiante:
    id: str
    correo: str
