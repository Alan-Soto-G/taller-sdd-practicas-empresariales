"""Adaptador en memoria de RepositorioPracticas (sustituye al Adaptador PostgreSQL en esta etapa; ADR-003)."""

from dominio.empresa import Empresa
from dominio.estado_postulacion import EstadoPostulacion
from dominio.estudiante import Estudiante
from dominio.plaza import Plaza
from dominio.postulacion import Postulacion
from dominio.practica import Practica
from dominio.regla_practica import ReglaPractica
from dominio.tutor import Tutor


class RepositorioPracticasMemoria:
    """Implementación en memoria del repositorio de prácticas."""

    def __init__(self) -> None:
        """Inicializa los almacenes en memoria."""
        self._plazas: dict[str, Plaza] = {}
        self._postulaciones: list[Postulacion] = []
        self._empresas: dict[str, Empresa] = {}
        self._reglas: dict[str, ReglaPractica] = {}
        self._version_vigente: str | None = None
        self._tutores: dict[str, Tutor] = {}
        self._estudiantes: dict[str, Estudiante] = {}
        self._practicas: dict[str, Practica] = {}

    def agregar_plaza(self, plaza: Plaza) -> None:
        """Precarga una plaza en el repositorio."""
        self._plazas[plaza.id] = plaza

    def obtener_plaza(self, id_plaza: str) -> Plaza | None:
        """Obtiene una plaza por su identificador."""
        return self._plazas.get(id_plaza)

    def contar_postulaciones_aceptadas(self, id_plaza: str) -> int:
        """Cuenta las postulaciones con estado ACEPTADA para una plaza."""
        return sum(
            1
            for p in self._postulaciones
            if p.id_plaza == id_plaza and p.estado == EstadoPostulacion.ACEPTADA
        )

    def tiene_postulacion_aceptada_en_periodo(self, id_estudiante: str, periodo: str) -> bool:
        """Indica si el estudiante ya cuenta con una postulación aceptada en el periodo."""
        return any(
            p.id_estudiante == id_estudiante
            and p.periodo == periodo
            and p.estado == EstadoPostulacion.ACEPTADA
            for p in self._postulaciones
        )

    def existe_postulacion(self, id_estudiante: str, id_plaza: str) -> bool:
        """Verifica si existe alguna postulación del estudiante a la plaza indicada."""
        return any(
            p.id_estudiante == id_estudiante and p.id_plaza == id_plaza
            for p in self._postulaciones
        )

    def guardar_postulacion(self, postulacion: Postulacion) -> None:
        """Agrega una postulación a la lista en memoria."""
        self._postulaciones.append(postulacion)

    def listar_postulaciones(self) -> list[Postulacion]:
        """Devuelve una copia de la lista de postulaciones registradas."""
        return list(self._postulaciones)

    def agregar_empresa(self, empresa: Empresa) -> None:
        """Precarga una empresa en el repositorio."""
        self._empresas[empresa.id] = empresa

    def obtener_empresa(self, id_empresa: str) -> Empresa | None:
        """Obtiene una empresa por su identificador."""
        return self._empresas.get(id_empresa)

    def guardar_plaza(self, plaza: Plaza) -> None:
        """Guarda una plaza nueva publicada por CU-02."""
        self._plazas[plaza.id] = plaza

    def listar_plazas(self) -> list[Plaza]:
        """Devuelve una copia de la lista de plazas registradas."""
        return list(self._plazas.values())

    def agregar_regla(self, regla: ReglaPractica, vigente: bool = True) -> None:
        """Guarda una regla de práctica por su versión."""
        self._reglas[regla.version] = regla
        if vigente:
            self._version_vigente = regla.version

    def obtener_regla_vigente(self) -> ReglaPractica:
        """Obtiene la regla de práctica vigente."""
        return self._reglas[self._version_vigente]

    def agregar_tutor(self, tutor: Tutor) -> None:
        """Precarga un tutor en el repositorio."""
        self._tutores[tutor.id] = tutor

    def obtener_tutor(self, id_tutor: str) -> Tutor | None:
        """Obtiene un tutor por su identificador."""
        return self._tutores.get(id_tutor)

    def agregar_estudiante(self, estudiante: Estudiante) -> None:
        """Precarga un estudiante en el repositorio."""
        self._estudiantes[estudiante.id] = estudiante

    def obtener_estudiante(self, id_estudiante: str) -> Estudiante | None:
        """Obtiene un estudiante por su identificador."""
        return self._estudiantes.get(id_estudiante)

    def agregar_practica(self, practica: Practica) -> None:
        """Precarga una práctica en el repositorio."""
        self._practicas[practica.id] = practica

    def obtener_practica(self, id_practica: str) -> Practica | None:
        """Obtiene una práctica por su identificador."""
        return self._practicas.get(id_practica)

    def contar_practicas_activas_tutor(self, id_tutor: str) -> int:
        """Cuenta las prácticas activas asignadas a un tutor."""
        return sum(
            1
            for p in self._practicas.values()
            if p.id_tutor == id_tutor and p.esta_activa()
        )

    def guardar_practica(self, practica: Practica) -> None:
        """Guarda una práctica en el repositorio."""
        self._practicas[practica.id] = practica

    def listar_practicas(self) -> list[Practica]:
        """Devuelve una copia de las prácticas registradas."""
        return list(self._practicas.values())
