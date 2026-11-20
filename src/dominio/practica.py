"""Practica: la practica de un Estudiante en una Empresa (vista logica, CU-03)."""

from dataclasses import dataclass, replace
from dominio.estado_practica import EstadoPractica


@dataclass(frozen=True)
class Practica:
    id: str
    id_estudiante: str
    id_empresa: str
    version_regla: str
    estado: EstadoPractica
    id_tutor: str | None = None

    def asignar_tutor(self, id_tutor: str) -> 'Practica':
        """Regla de CU-03: solo una Practica sin tutor recibe tutor y pasa a en curso."""
        if self.estado != EstadoPractica.SIN_TUTOR:
            raise ValueError('la practica ya tiene tutor')
        return replace(self, id_tutor=id_tutor, estado=EstadoPractica.EN_CURSO)

    def esta_activa(self) -> bool:
        """Una Practica cuenta en la carga del tutor mientras no este cerrada."""
        return self.estado != EstadoPractica.CERRADA
