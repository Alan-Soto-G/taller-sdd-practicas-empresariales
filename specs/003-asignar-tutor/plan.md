# Plan: 003 Asignar tutor a un estudiante

Aterriza [spec.md](spec.md) (CU-03) en la arquitectura de [docs/arquitectura.md](../../docs/arquitectura.md). No agrega componentes fuera de [vistas/03-desarrollo.md](../../docs/vistas/03-desarrollo.md) y reutiliza lo construido en [001](../001-postularse-plaza-practica/plan.md) y [002](../002-publicar-plaza-practica/plan.md) sin cambiar su comportamiento.

## Decisiones que aplican

| ID | Qué aplica a CU-03 |
|----|--------------------|
| ADR-002 | El caso de uso vive en el **Módulo Asignación** (`src/aplicacion/asignacion/`). Según la vista de usos, Asignación usa el **Módulo Configuración** para leer la carga máxima por tutor: se crea `src/aplicacion/configuracion/` con la consulta de la ReglaPractica vigente. `dominio/` no importa nada de las otras capas. Puertos como `Protocol` en `aplicacion/puertos/`. |
| ADR-003 | El Adaptador PostgreSQL implementa RepositorioPracticas; en esta etapa se amplía el adaptador en memoria. |
| ADR-004 | El Validador de token entrega identidad y rol. La autorización por rol (solo `CoordinadorPracticas` asigna) se hace en el caso de uso. |
| ADR-006 | Se audita el cambio de estado de cada Práctica ("sin tutor" → "en curso") y cada acceso rechazado, con usuario, rol, recurso, acción y hora. Los resultados "no asignada" no se auditan. |
| ADR-007 | Errores de aplicación propios (`TutorNoEncontrado`, `CorreoNoEnviado`). El adaptador de correo traduce su falla a `CorreoNoEnviado` y deja la notificación pendiente de reenvío; el caso de uso no revierte la asignación. El controlador da la respuesta unificada. |
| ADR-008 | La carga máxima por tutor es un dato de la ReglaPractica vigente; cambiarla no exige programar (escenario del cambio a "v2"). Cada Practica guarda la versión de ReglaPractica con la que empezó. |
| Vista lógica | Practica (estado, tutor, versión de regla), EstadoPractica (ciclo de vida), Tutor (regla de carga máxima), Estudiante, ReglaPractica (versión, horas requeridas, carga máxima por tutor, plantilla del acta). |
| Vista de desarrollo | Controlador REST, Validador de token, Módulo Asignación, Módulo Configuración, puertos RepositorioPracticas, Notificador y Bitacora, sus adaptadores en memoria o simulados y `main.py`. |

## Componentes

Python 3.12, una clase por archivo, sin `__init__.py`, nombres del glosario. **(nuevo)** o **(cambia)** en cada archivo.

### dominio (`src/dominio/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `estado_practica.py` **(nuevo)** | `EstadoPractica` (StrEnum) | `SIN_TUTOR="sin tutor"`, `EN_CURSO="en curso"`, `HORAS_COMPLETAS="horas completas"`, `EVALUADA="evaluada"`, `ACTA_EN_TRAMITE="acta en trámite"`, `CERRADA="cerrada"` |
| `practica.py` **(nuevo)** | `Practica` (dataclass frozen) | `id`, `id_estudiante`, `id_empresa`, `version_regla`, `estado`, `id_tutor: str \| None = None`. `asignar_tutor(id_tutor) -> Practica`: devuelve una copia con el tutor y estado `EN_CURSO`; lanza `ValueError` si el estado no es `SIN_TUTOR`. `esta_activa() -> bool`: estado distinto de `CERRADA` |
| `tutor.py` **(nuevo)** | `Tutor` (dataclass frozen) | `id`, `correo`. `tiene_cupo(carga_actual, carga_maxima) -> bool`: `carga_actual < carga_maxima` (vista lógica: atiende como máximo la carga de ReglaPractica) |
| `estudiante.py` **(nuevo)** | `Estudiante` (dataclass frozen) | `id`, `correo` |
| `regla_practica.py` **(nuevo)** | `ReglaPractica` (dataclass frozen) | `version`, `horas_requeridas`, `carga_maxima_tutor`, `plantilla_acta` |

### aplicacion (`src/aplicacion/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `errores/tutor_no_encontrado.py` **(nuevo)** | `TutorNoEncontrado` | código `tutor_no_encontrado`, mensaje "tutor no encontrado" |
| `errores/correo_no_enviado.py` **(nuevo)** | `CorreoNoEnviado` | código `correo_no_enviado`, mensaje "correo no enviado" (ADR-007) |
| `puertos/notificador.py` **(nuevo)** | `Notificador` (Protocol) | `enviar(destinatarios: list[str], asunto: str, mensaje: str) -> None`; lanza `CorreoNoEnviado` si falla |
| `puertos/repositorio_practicas.py` **(cambia)** | `RepositorioPracticas` | Agrega `obtener_regla_vigente() -> ReglaPractica`, `obtener_tutor(id) -> Tutor \| None`, `obtener_estudiante(id) -> Estudiante \| None`, `obtener_practica(id) -> Practica \| None`, `contar_practicas_activas_tutor(id_tutor) -> int`, `guardar_practica(practica) -> None` |
| `configuracion/regla_vigente.py` **(nuevo)** | `ReglaVigente` (DTO de salida) | `version`, `horas_requeridas`, `carga_maxima_tutor`, `plantilla_acta` |
| `configuracion/consultar_regla_vigente.py` **(nuevo)** | `ConsultarReglaVigente` | Caso de uso del Módulo Configuración: lee la ReglaPractica vigente del repositorio y la devuelve como `ReglaVigente` |
| `asignacion/solicitud_asignacion_tutor.py` **(nuevo)** | `SolicitudAsignacionTutor` (DTO de entrada) | `usuario`, `id_tutor`, `ids_practicas: tuple[str, ...]` |
| `asignacion/resultado_practica.py` **(nuevo)** | `ResultadoPractica` (DTO) | `id_practica`, `resultado` ("asignada" o "no asignada: <motivo>") |
| `asignacion/asignacion_realizada.py` **(nuevo)** | `AsignacionRealizada` (DTO de salida) | `id_tutor`, `resultados: tuple[ResultadoPractica, ...]` |
| `asignacion/asignar_tutor.py` **(nuevo)** | `AsignarTutor` | Caso de uso de CU-03 (ver Flujo). Recibe `RepositorioPracticas`, `Bitacora`, `Notificador`, `ConsultarReglaVigente` y un `reloj` |

Se reutilizan sin cambios: `Bitacora`, `UsuarioAutenticado`, `ErrorAplicacion`, `NoAutenticado`, `AccesoDenegado`.

### infraestructura (`src/infraestructura/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `notificador_simulado.py` **(nuevo)** | `NotificadorSimulado` | Sustituye al Adaptador de correo. Atributo `disponible` (por defecto `True`). Si está disponible, agrega el correo a `enviados`; si no, lo agrega a `pendientes` (para reenvío) y lanza `CorreoNoEnviado`. `listar_enviados()` y `listar_pendientes()` para la evidencia |
| `repositorio_practicas_memoria.py` **(cambia)** | `RepositorioPracticasMemoria` | Agrega almacenes de reglas (con la versión vigente), tutores, estudiantes y prácticas; `agregar_regla(regla, vigente=True)`, `agregar_tutor`, `agregar_estudiante`, `agregar_practica` para precargar; los métodos nuevos del puerto y `listar_practicas()` |
| `controlador_rest.py` **(cambia)** | `ControladorRest` | Recibe también `AsignarTutor`. `asignar_tutor(token, cuerpo)` representa "POST /asignaciones": cuerpo `id_tutor` e `ids_practicas` (lista); responde 200 con `id_tutor`, `resultados` (lista de `{id_practica, resultado}`) y el mensaje "asignación procesada". Agrega 404 para `TutorNoEncontrado` |
| `src/main.py` **(cambia)** | (composición) | Crea `NotificadorSimulado`, `ConsultarReglaVigente` y `AsignarTutor`. Precarga la ReglaPractica "v1" (horas requeridas 160 como dato de prueba, carga máxima 2, plantilla "plantilla-acta-v1"), los Tutores "T-200" y "T-300", los Estudiantes "E-1001", "E-1002" y "E-1003" con sus correos, y las Practicas "PR-01" y "PR-02" ("sin tutor") y "PR-03" ("en curso" con "T-300"), todas de "EMP-ACME" con la regla "v1". Expone `notificador` en el diccionario |

Vista de usos: Módulo Asignación → Módulo Configuración → dominio. Configuración no usa otros módulos: no hay ciclos.

## Flujo

Secuencia [cu03-asignar-tutor.puml](../../docs/diagramas/secuencias/cu03-asignar-tutor.puml) (ESC-02):

1. `ControladorRest.asignar_tutor` recibe "POST /asignaciones" con el token y el cuerpo.
2. `ValidadorToken` valida el token (15 minutos). Si falla, 401 sin llamar al caso de uso.
3. `AsignarTutor.ejecutar(SolicitudAsignacionTutor)`:
   1. Si el rol no es `CoordinadorPracticas`: registra en la `Bitacora` un acceso rechazado por cada práctica pedida (recurso `practica:<id>`, acción "asignar tutor") y lanza `AccesoDenegado`.
   2. Obtiene el `Tutor`; si no existe, lanza `TutorNoEncontrado`.
   3. Lee la carga máxima con `ConsultarReglaVigente` y la carga actual con `contar_practicas_activas_tutor`.
   4. Por cada práctica, en el orden recibido:
      - no existe → "no asignada: práctica no encontrada";
      - estado distinto de "sin tutor" → "no asignada: la práctica ya tiene tutor";
      - `not tutor.tiene_cupo(carga, carga_maxima)` → "no asignada: tutor sin cupo";
      - si no: `practica.asignar_tutor`, `guardar_practica`, registro en la bitácora (recurso `practica:<id>`, acción "cambiar estado de sin tutor a en curso"), carga + 1, y notificación al tutor y al estudiante con `Notificador.enviar`; si lanza `CorreoNoEnviado`, se ignora (queda pendiente en el adaptador). Resultado "asignada".
   5. Devuelve `AsignacionRealizada`.
4. `ControladorRest` responde 200 o traduce el error (ADR-007).

## Fuera de alcance

- Reasignar o quitar el tutor de una práctica que ya lo tiene.
- Crear la Práctica al aceptar una Postulacion (ningún CU del catálogo lo cubre): las prácticas se precargan.
- Administrar versiones de ReglaPractica desde la API: la regla se precarga; el cambio a "v2" del escenario se hace con `agregar_regla` en la validación.
- Reenvío real de correos pendientes, servidor HTTP real, PostgreSQL y SMTP: adaptadores en memoria o simulados.
- Aplicación web (ADR-010) y pruebas automatizadas.
