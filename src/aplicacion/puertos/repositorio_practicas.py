"""Puerto de persistencia de las entidades del proceso (glosario: RepositorioPracticas; ADR-003). Lo implementa infraestructura."""
from typing import Protocol

from dominio.empresa import Empresa
from dominio.estudiante import Estudiante
from dominio.registro_horas import RegistroHoras
from dominio.plaza import Plaza
from dominio.postulacion import Postulacion
from dominio.practica import Practica
from dominio.regla_practica import ReglaPractica
from dominio.tutor import Tutor


class RepositorioPracticas(Protocol):
    def obtener_plaza(self, id_plaza: str) -> Plaza | None:
        """Devuelve la Plaza o None si no existe."""
        ...

    def contar_postulaciones_aceptadas(self, id_plaza: str) -> int:
        """Cuenta las Postulaciones aceptadas de la Plaza."""
        ...

    def tiene_postulacion_aceptada_en_periodo(self, id_estudiante: str, periodo: str) -> bool:
        """Indica si el Estudiante tiene una Postulacion aceptada en el periodo."""
        ...

    def existe_postulacion(self, id_estudiante: str, id_plaza: str) -> bool:
        """Indica si el Estudiante ya tiene una Postulacion a la Plaza, en cualquier estado."""
        ...

    def guardar_postulacion(self, postulacion: Postulacion) -> None:
        """Guarda una Postulacion nueva."""
        ...

    def obtener_empresa(self, id_empresa: str) -> Empresa | None:
        """Devuelve la Empresa o None si no existe (CU-02)."""
        ...

    def guardar_plaza(self, plaza: Plaza) -> None:
        """Guarda una Plaza nueva (CU-02)."""
        ...

    def obtener_regla_vigente(self) -> ReglaPractica:
        """Devuelve la ReglaPractica vigente (CU-03, ADR-008)."""
        ...

    def obtener_tutor(self, id_tutor: str) -> Tutor | None:
        """Devuelve el Tutor o None si no existe (CU-03)."""
        ...

    def obtener_estudiante(self, id_estudiante: str) -> Estudiante | None:
        """Devuelve el Estudiante o None si no existe (CU-03)."""
        ...

    def obtener_practica(self, id_practica: str) -> Practica | None:
        """Devuelve la Practica o None si no existe (CU-03)."""
        ...

    def contar_practicas_activas_tutor(self, id_tutor: str) -> int:
        """Cuenta las Practicas del Tutor que no estan cerradas (CU-03)."""
        ...

    def guardar_practica(self, practica: Practica) -> None:
        """Guarda la Practica, nueva o modificada (CU-03)."""
        ...

    def existe_registro_horas(self, id_practica: str, semana: str) -> bool:
        """Indica si la Practica ya tiene un RegistroHoras de la semana (CU-04)."""
        ...

    def guardar_registro_horas(self, registro: RegistroHoras) -> bool:
        """Guarda el RegistroHoras de forma atomica; devuelve False, sin guardar, si ya hay uno de la misma Practica y semana (CU-04, EAC-01)."""
        ...
