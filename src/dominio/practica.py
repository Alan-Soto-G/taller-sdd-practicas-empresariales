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
    def completar_horas(self) -> 'Practica':
        """Regla de CU-05: una Practica en curso pasa a horas completas cuando sus horas aprobadas alcanzan las requeridas."""
        if self.estado != EstadoPractica.EN_CURSO:
            raise ValueError('la practica no esta en curso')
        return replace(self, estado=EstadoPractica.HORAS_COMPLETAS)

    def evaluar(self) -> 'Practica':
        """Regla de CU-06: una Practica con horas completas pasa a evaluada al registrarse la evaluacion de la empresa."""
        if self.estado != EstadoPractica.HORAS_COMPLETAS:
            raise ValueError('la practica no tiene las horas completas')
        return replace(self, estado=EstadoPractica.EVALUADA)

    def solicitar_acta(self) -> 'Practica':
        """Regla de CU-07: una Practica evaluada pasa a acta en tramite al solicitar su acta final."""
        if self.estado != EstadoPractica.EVALUADA:
            raise ValueError('la practica no esta evaluada')
        return replace(self, estado=EstadoPractica.ACTA_EN_TRAMITE)
