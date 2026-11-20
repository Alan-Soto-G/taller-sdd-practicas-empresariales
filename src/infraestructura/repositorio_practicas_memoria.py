"""Adaptador en memoria de RepositorioPracticas (sustituye al Adaptador PostgreSQL en esta etapa; ADR-003)."""

from threading import Lock

from dominio.acta_final import ActaFinal
from dominio.aprobacion import Aprobacion
from dominio.coordinador_practicas import CoordinadorPracticas
from dominio.empresa import Empresa
from dominio.enlace_acceso import EnlaceAcceso
from dominio.estado_postulacion import EstadoPostulacion
from dominio.estado_registro_horas import EstadoRegistroHoras
from dominio.estudiante import Estudiante
from dominio.evaluacion import Evaluacion
from dominio.intento_generacion import IntentoGeneracion
from dominio.plaza import Plaza
from dominio.postulacion import Postulacion
from dominio.practica import Practica
from dominio.registro_horas import RegistroHoras
from dominio.regla_practica import ReglaPractica
from dominio.representante_empresa import RepresentanteEmpresa
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
        self._registros_horas: list[RegistroHoras] = []
        self._candado_horas = Lock()
        self._representantes: dict[str, RepresentanteEmpresa] = {}
        self._enlaces: dict[str, EnlaceAcceso] = {}
        self._evaluaciones: list[Evaluacion] = []
        self._candado_enlaces = Lock()
        self._actas: dict[str, ActaFinal] = {}
        self._intentos: list[IntentoGeneracion] = []
        self._coordinador: CoordinadorPracticas | None = None
        self._candado_actas = Lock()
        self._aprobaciones: list[Aprobacion] = []

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

    def existe_registro_horas(self, id_practica: str, semana: str) -> bool:
        """Indica si existe un registro de horas para la práctica y semana."""
        return any(
            r.id_practica == id_practica and r.semana == semana
            for r in self._registros_horas
        )

    def guardar_registro_horas(self, registro: RegistroHoras) -> bool:
        """Guarda de forma atomica (equivale a la restriccion unica de PostgreSQL); False si ya hay un registro de la practica y la semana."""
        with self._candado_horas:
            if self.existe_registro_horas(registro.id_practica, registro.semana):
                return False
            self._registros_horas.append(registro)
            return True

    def listar_registros_horas(self) -> list[RegistroHoras]:
        """Devuelve una copia de la lista de registros de horas."""
        return list(self._registros_horas)

    def obtener_regla(self, version: str) -> ReglaPractica | None:
        """Obtiene una regla de práctica por su versión."""
        return self._reglas.get(version)

    def obtener_registro_horas(self, id_registro: str) -> RegistroHoras | None:
        """Obtiene un registro de horas por su identificador."""
        for r in self._registros_horas:
            if r.id == id_registro:
                return r
        return None

    def actualizar_registro_horas(self, registro: RegistroHoras) -> None:
        """Actualiza un registro de horas existente."""
        with self._candado_horas:
            for idx, r in enumerate(self._registros_horas):
                if r.id == registro.id:
                    self._registros_horas[idx] = registro
                    break

    def sumar_horas_aprobadas(self, id_practica: str) -> int:
        """Calcula el total de horas aprobadas para una práctica."""
        return sum(
            r.horas
            for r in self._registros_horas
            if r.id_practica == id_practica and r.estado == EstadoRegistroHoras.APROBADO
        )

    def agregar_representante(self, representante: RepresentanteEmpresa) -> None:
        """Precarga un representante de empresa en el repositorio."""
        self._representantes[representante.id] = representante

    def obtener_representante_de_empresa(
        self, id_empresa: str
    ) -> RepresentanteEmpresa | None:
        """Obtiene el primer representante asociado a una empresa."""
        return next(
            (
                representante
                for representante in self._representantes.values()
                if representante.id_empresa == id_empresa
            ),
            None,
        )

    def guardar_enlace(self, enlace: EnlaceAcceso) -> None:
        """Guarda un enlace de acceso en el repositorio."""
        self._enlaces[enlace.id] = enlace

    def obtener_enlace_por_token(self, token: str) -> EnlaceAcceso | None:
        """Obtiene el primer enlace de acceso con el token indicado."""
        return next(
            (enlace for enlace in self._enlaces.values() if enlace.token == token),
            None,
        )

    def invalidar_enlaces(self, id_practica: str, accion: str) -> None:
        """Invalida los enlaces no usados de una práctica y acción."""
        with self._candado_enlaces:
            for enlace in list(self._enlaces.values()):
                if (
                    enlace.id_practica == id_practica
                    and enlace.accion == accion
                    and not enlace.usado
                ):
                    self._enlaces[enlace.id] = enlace.usar()

    def marcar_enlace_usado(self, id_enlace: str) -> bool:
        """Marca el enlace como usado de forma atomica (un solo uso, ADR-005)."""
        with self._candado_enlaces:
            enlace = self._enlaces.get(id_enlace)
            if enlace is None or enlace.usado:
                return False
            self._enlaces[id_enlace] = enlace.usar()
            return True

    def guardar_evaluacion(self, evaluacion: Evaluacion) -> None:
        """Guarda una evaluación en el repositorio."""
        self._evaluaciones.append(evaluacion)

    def listar_enlaces(self) -> list[EnlaceAcceso]:
        """Devuelve una copia de los enlaces registrados."""
        return list(self._enlaces.values())

    def listar_evaluaciones(self) -> list[Evaluacion]:
        """Devuelve una copia de las evaluaciones registradas."""
        return list(self._evaluaciones)

    def guardar_acta(self, acta: ActaFinal) -> None:
        """Guarda un acta final en el repositorio."""
        with self._candado_actas:
            self._actas[acta.id] = acta

    def obtener_acta(self, id_acta: str) -> ActaFinal | None:
        """Obtiene un acta final por su identificador."""
        return self._actas.get(id_acta)

    def guardar_intento(self, intento: IntentoGeneracion) -> None:
        """Guarda un intento de generación de acta."""
        with self._candado_actas:
            self._intentos.append(intento)

    def obtener_evaluacion_de_practica(
        self, id_practica: str
    ) -> Evaluacion | None:
        """Obtiene la primera evaluación de una práctica."""
        return next(
            (
                evaluacion
                for evaluacion in self._evaluaciones
                if evaluacion.id_practica == id_practica
            ),
            None,
        )

    def agregar_coordinador(self, coordinador: CoordinadorPracticas) -> None:
        """Precarga el coordinador de prácticas."""
        self._coordinador = coordinador

    def obtener_coordinador(self) -> CoordinadorPracticas | None:
        """Obtiene el coordinador de prácticas precargado."""
        return self._coordinador

    def listar_actas(self) -> list[ActaFinal]:
        """Devuelve una copia de las actas registradas."""
        return list(self._actas.values())

    def listar_intentos(
        self, id_acta: str | None = None
    ) -> list[IntentoGeneracion]:
        """Devuelve los intentos, opcionalmente filtrados por acta."""
        if id_acta is None:
            return list(self._intentos)
        return [intento for intento in self._intentos if intento.id_acta == id_acta]

    def guardar_aprobacion(self, aprobacion: Aprobacion) -> None:
        """Registra una aprobación del acta."""
        with self._candado_actas:
            self._aprobaciones.append(aprobacion)

    def listar_aprobaciones(self, id_acta: str) -> list[Aprobacion]:
        """Devuelve las aprobaciones del acta."""
        return [a for a in self._aprobaciones if a.id_acta == id_acta]

    def obtener_acta_de_practica(self, id_practica: str) -> ActaFinal | None:
        """Devuelve el acta más reciente de la práctica, o None."""
        actas = [a for a in self._actas.values() if a.id_practica == id_practica]
        return max(actas, key=lambda a: a.fecha_solicitud) if actas else None

    def listar_practicas_de_tutor(self, id_tutor: str) -> list[Practica]:
        """Devuelve las prácticas asignadas al tutor, ordenadas por id."""
        return sorted(
            (p for p in self._practicas.values() if p.id_tutor == id_tutor),
            key=lambda p: p.id,
        )

    def listar_registros_horas_de_practica(self, id_practica: str) -> list[RegistroHoras]:
        """Devuelve los registros de horas de la práctica."""
        return [r for r in self._registros_horas if r.id_practica == id_practica]

    def listar_practicas_de_estudiante(self, id_estudiante: str) -> list[Practica]:
        """Devuelve las prácticas del estudiante, ordenadas por id."""
        return sorted(
            (p for p in self._practicas.values() if p.id_estudiante == id_estudiante),
            key=lambda p: p.id,
        )

    def guardar_empresa(self, empresa: Empresa) -> None:
        """Guarda una empresa, nueva o modificada."""
        self._empresas[empresa.id] = empresa

    def guardar_tutor(self, tutor: Tutor) -> None:
        """Guarda un tutor nuevo."""
        self._tutores[tutor.id] = tutor

    def guardar_estudiante(self, estudiante: Estudiante) -> None:
        """Guarda un estudiante nuevo."""
        self._estudiantes[estudiante.id] = estudiante

    def listar_empresas(self) -> list[Empresa]:
        """Devuelve una copia de las empresas registradas."""
        return list(self._empresas.values())

    def eliminar_empresa(self, id_empresa: str) -> None:
        """Elimina la empresa y su representante."""
        self._empresas.pop(id_empresa, None)
        for id_representante in [r.id for r in self._representantes.values() if r.id_empresa == id_empresa]:
            del self._representantes[id_representante]

    def guardar_representante(self, representante: RepresentanteEmpresa) -> None:
        """Guarda un representante, nuevo o modificado."""
        self._representantes[representante.id] = representante
