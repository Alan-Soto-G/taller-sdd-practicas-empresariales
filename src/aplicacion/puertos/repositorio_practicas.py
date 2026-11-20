"""Puerto de persistencia de las entidades del proceso (glosario: RepositorioPracticas; ADR-003). Lo implementa infraestructura."""
from typing import Protocol

from dominio.empresa import Empresa
from dominio.plaza import Plaza
from dominio.postulacion import Postulacion


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
