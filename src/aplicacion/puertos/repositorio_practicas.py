"""Puerto de persistencia de las entidades del proceso (glosario: RepositorioPracticas; ADR-003). Lo implementa infraestructura."""
from typing import Protocol

from dominio.acta_final import ActaFinal
from dominio.coordinador_practicas import CoordinadorPracticas
from dominio.empresa import Empresa
from dominio.enlace_acceso import EnlaceAcceso
from dominio.estudiante import Estudiante
from dominio.evaluacion import Evaluacion
from dominio.intento_generacion import IntentoGeneracion
from dominio.registro_horas import RegistroHoras
from dominio.plaza import Plaza
from dominio.postulacion import Postulacion
from dominio.practica import Practica
from dominio.regla_practica import ReglaPractica
from dominio.representante_empresa import RepresentanteEmpresa
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

    def obtener_regla(self, version: str) -> ReglaPractica | None:
        """Devuelve la ReglaPractica de esa version o None (CU-05, ADR-008)."""
        ...

    def obtener_registro_horas(self, id_registro: str) -> RegistroHoras | None:
        """Devuelve el RegistroHoras o None si no existe (CU-05)."""
        ...

    def actualizar_registro_horas(self, registro: RegistroHoras) -> None:
        """Reemplaza el RegistroHoras con el mismo id (CU-05)."""
        ...

    def sumar_horas_aprobadas(self, id_practica: str) -> int:
        """Suma las horas de los RegistroHoras aprobados de la Practica (CU-05)."""
        ...

    def obtener_representante_de_empresa(self, id_empresa: str) -> RepresentanteEmpresa | None:
        """Devuelve el RepresentanteEmpresa de la Empresa o None (CU-06)."""
        ...

    def guardar_enlace(self, enlace: EnlaceAcceso) -> None:
        """Guarda un EnlaceAcceso nuevo (CU-06, ADR-005)."""
        ...

    def obtener_enlace_por_token(self, token: str) -> EnlaceAcceso | None:
        """Devuelve el EnlaceAcceso del token o None (ADR-005)."""
        ...

    def invalidar_enlaces(self, id_practica: str, accion: str) -> None:
        """Marca como usados los enlaces sin usar de la Practica para la accion; se usa al reemitir (ADR-005)."""
        ...

    def marcar_enlace_usado(self, id_enlace: str) -> bool:
        """Marca el enlace como usado de forma atomica; devuelve False si ya estaba usado (un solo uso, ADR-005)."""
        ...

    def guardar_evaluacion(self, evaluacion: Evaluacion) -> None:
        """Guarda la Evaluacion de la Practica (CU-06)."""
        ...

    def guardar_acta(self, acta: ActaFinal) -> None:
        """Guarda el ActaFinal, nueva o modificada (CU-07)."""
        ...

    def obtener_acta(self, id_acta: str) -> ActaFinal | None:
        """Devuelve el ActaFinal o None si no existe (CU-07)."""
        ...

    def guardar_intento(self, intento: IntentoGeneracion) -> None:
        """Registra un IntentoGeneracion del Worker de actas (CU-07, ADR-001)."""
        ...

    def obtener_evaluacion_de_practica(self, id_practica: str) -> Evaluacion | None:
        """Devuelve la Evaluacion de la Practica o None (CU-07)."""
        ...

    def obtener_coordinador(self) -> CoordinadorPracticas | None:
        """Devuelve el Coordinador de Practicas o None (CU-07)."""
        ...
