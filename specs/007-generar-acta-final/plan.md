# Plan: 007 Generar el acta final

Aterriza [spec.md](spec.md) (CU-07) en la arquitectura de [docs/arquitectura.md](../../docs/arquitectura.md). No agrega componentes fuera de [vistas/02-procesos.md](../../docs/vistas/02-procesos.md) y [vistas/03-desarrollo.md](../../docs/vistas/03-desarrollo.md), y reutiliza lo construido en 001 a 006 sin cambiar su comportamiento.

## Decisiones que aplican

| ID | Qué aplica a CU-07 |
|----|--------------------|
| ADR-001 | La API **solo encola**: `SolicitarActas` registra el ActaFinal "en generación" y publica una `SolicitudActa` con el puerto `PublicadorActas`. El **Worker de actas** consume la cola `actas`, genera el acta con hasta 3 intentos y esperas de 1 y 2 min, y manda a `errores_actas` lo que agota los intentos. |
| ADR-002 | Los casos de uso viven en el **Módulo Actas** (`src/aplicacion/actas/`). El Worker de actas es otro proceso con su propia composición (`src/worker.py`), que reutiliza `dominio/`, el caso de uso de generación (`GenerarActa`) y los adaptadores. |
| ADR-003 | El PDF se guarda con el puerto `AlmacenActas` (Repositorio de actas) y en la base solo queda su ruta. En esta etapa, la cola y el almacén son adaptadores en memoria. |
| ADR-004 | Solo `CoordinadorPracticas` solicita actas; la autorización está en el caso de uso. |
| ADR-006 | Se auditan la creación del ActaFinal, el cambio de la Práctica, los cambios del acta hechos por el Worker y cada acceso rechazado. `IntentoGeneracion` deja rastro de cada intento. |
| ADR-007 | El almacén traduce su falla a `AlmacenNoDisponible`; el Worker la registra como intento fallido. Si el correo de aviso falla, el acta sigue "generada". |
| ADR-008 | El acta usa la plantilla de la versión de ReglaPractica de la Práctica. |
| ADR-011 | Resuelve DT-05: el PDF lo compone **ReportLab 5.1.0** detrás del puerto `ComponedorActa` (`aplicacion/puertos/`), implementado por `ComponedorActaReportlab` (`infraestructura/`). Solo el Worker lo compone. Las fallas de la librería se traducen a `ActaNoComponible`, que cuenta como intento fallido. Versión fijada en `src/requirements.txt`. La primera versión de este plan usaba un documento simulado (T-16); el ajuste son las tareas T-25 a T-32. |
| Vista lógica | ActaFinal, IntentoGeneracion, CoordinadorPracticas, la transición "evaluada" → "acta en trámite" y el mensaje `SolicitudActa`. |

## Componentes

Python 3.12, una clase por archivo, sin `__init__.py`. **(nuevo)** o **(cambia)**.

### dominio (`src/dominio/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `estado_acta.py` **(nuevo)** | `EstadoActa` (StrEnum) | `EN_GENERACION="en generación"`, `GENERADA="generada"`, `APROBADA="aprobada"`, `CON_ERROR="con error"` |
| `acta_final.py` **(nuevo)** | `ActaFinal` | `id`, `id_practica`, `fecha_solicitud`, `estado`, `ruta_pdf=None`. `solicitar(id, id_practica, ahora)` (classmethod) crea el acta en "en generación"; `marcar_generada(ruta)` y `marcar_con_error()` solo desde "en generación" (`ValueError` si no) |
| `intento_generacion.py` **(nuevo)** | `IntentoGeneracion` | `id_acta`, `numero`, `fecha`, `resultado`. `MAX_INTENTOS = 3`. `espera_tras(numero) -> timedelta` (staticmethod): 1 min tras el intento 1 y 2 min tras el 2 (ADR-001) |
| `coordinador_practicas.py` **(nuevo)** | `CoordinadorPracticas` | `id`, `correo` |
| `practica.py` **(cambia)** | `Practica` | `solicitar_acta()`: copia en `ACTA_EN_TRAMITE`; `ValueError` si no está `EVALUADA` |

### aplicacion (`src/aplicacion/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `actas/solicitud_acta.py` **(nuevo)** | `SolicitudActa` (mensaje) | `id_acta`, `id_practica`, `intento` (glosario: mensaje `SolicitudActa`) |
| `errores/almacen_no_disponible.py` **(nuevo)** | `AlmacenNoDisponible` | código `almacen_no_disponible`, mensaje "repositorio de actas no disponible" |
| `puertos/publicador_actas.py` **(nuevo)** | `PublicadorActas` (Protocol) | `publicar(solicitud: SolicitudActa) -> None` |
| `puertos/almacen_actas.py` **(nuevo)** | `AlmacenActas` (Protocol) | `guardar(id_acta, contenido: bytes) -> str` (ruta) y `leer(ruta) -> bytes`; lanzan `AlmacenNoDisponible` |
| `puertos/repositorio_practicas.py` **(cambia)** | `RepositorioPracticas` | Agrega `guardar_acta`, `obtener_acta`, `guardar_intento`, `obtener_evaluacion_de_practica` y `obtener_coordinador` |
| `actas/solicitud_generacion_actas.py` **(nuevo)** | `SolicitudGeneracionActas` (DTO) | `usuario`, `ids_practicas` |
| `actas/resultado_solicitud_acta.py` **(nuevo)** | `ResultadoSolicitudActa` (DTO) | `id_practica`, `id_acta \| None`, `resultado` |
| `actas/actas_solicitadas.py` **(nuevo)** | `ActasSolicitadas` (DTO) | `resultados` |
| `actas/solicitar_actas.py` **(nuevo)** | `SolicitarActas` | Lado API (ver Flujo). Recibe repositorio, bitacora, publicador y reloj |
| `actas/resultado_generacion.py` **(nuevo)** | `ResultadoGeneracion` (DTO) | `id_acta`, `estado` ("generada", "reintentar", "con error" u "omitida"), `espera: timedelta \| None` |
| `actas/generar_acta.py` **(nuevo)** | `GenerarActa` | Lado Worker (ver Flujo). Recibe repositorio, bitacora, almacén, notificador y reloj |

### infraestructura (`src/infraestructura/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `cola_actas_memoria.py` **(nuevo)** | `ColaActasMemoria` | Sustituye al Broker (RabbitMQ) y al Publicador. `publicar` (implementa `PublicadorActas`; disponible desde ya), `tomar(ahora)` (la primera solicitud disponible o `None`), `reencolar(solicitud, disponible_desde)`, `enviar_a_errores(solicitud)`, `listar_actas()` y `listar_errores()`. Con `Lock` |
| `almacen_actas_memoria.py` **(nuevo)** | `AlmacenActasMemoria` | Sustituye al Repositorio de actas. `fallas_pendientes` (por defecto 0): mientras sea mayor que 0, `guardar` la descuenta y lanza `AlmacenNoDisponible`. Si no, guarda en `actas/<id_acta>.pdf` y devuelve la ruta. `leer` y `listar()` |
| `worker_actas.py` **(nuevo)** | `WorkerActas` | Adaptador de entrada del Worker: `procesar(ahora)` toma de la cola mientras haya solicitudes disponibles y llama `GenerarActa`. Con "reintentar" reencola el intento siguiente para `ahora + espera`; con "con error" la envía a `errores_actas`. Devuelve cuántas procesó |
| `repositorio_practicas_memoria.py` **(cambia)** | `RepositorioPracticasMemoria` | Actas, intentos, coordinador y evaluación por práctica; `agregar_coordinador`, `listar_actas`, `listar_intentos` |
| `controlador_rest.py` **(cambia)** | `ControladorRest` | Recibe `SolicitarActas`. `solicitar_actas(token, cuerpo)` representa "POST /actas" con `ids_practicas`: 202 con los resultados y el mensaje "actas en generación; se le notificará" |
| `src/main.py` **(cambia)** | (composición de la API) | Crea `ColaActasMemoria`, `AlmacenActasMemoria` y `SolicitarActas`. Precarga el Coordinador "C-01" con su correo, el Estudiante "E-1008", la Practica "PR-08" ("evaluada", "T-400", "v1"), 8 RegistroHoras aprobados de 20 horas, la Evaluacion de "PR-08" y el token `tok-T-400` |
| `src/worker.py` **(nuevo)** | (composición del Worker) | `construir_worker(repositorio, bitacora, notificador, cola, almacen, reloj)` crea `GenerarActa` y `WorkerActas`. En producción comparte PostgreSQL y el broker; en esta etapa recibe los mismos adaptadores en memoria que la API |

## Flujo

Secuencia [cu07-generar-acta-final.puml](../../docs/diagramas/secuencias/cu07-generar-acta-final.puml) (ESC-05):

1. **API** (`SolicitarActas`):
   - rol distinto de Coordinador → bitácora por cada práctica (`practica:<id>`, "solicitar acta") y `AccesoDenegado`;
   - por cada práctica: si no existe → "no solicitada: práctica no encontrada"; si no está "evaluada" → "no solicitada: la práctica no está evaluada";
   - si todo va bien: crea `ActaFinal` con id `AC-<8 hex>` y la guarda; pasa la Práctica a "acta en trámite"; audita ambos cambios; publica `SolicitudActa(acta, practica, 1)`; resultado "en generación".
2. **Worker** (`WorkerActas.procesar` → `GenerarActa.ejecutar(SolicitudActa)`):
   - si el acta no está "en generación" → "omitida" (idempotencia);
   - consolida la práctica, las horas aprobadas, la Evaluacion, la ReglaPractica de su versión, el tutor, el representante y el coordinador, arma `DatosActa` y pide el PDF al `ComponedorActa` (ADR-011);
   - `almacen.guardar` → `IntentoGeneracion(numero, "exitoso")`, `acta.marcar_generada(ruta)`, bitácora ("cambiar estado de en generación a generada") y aviso por correo (ignora `CorreoNoEnviado`) → "generada";
   - si `AlmacenNoDisponible` → `IntentoGeneracion(numero, "fallido: <mensaje>")`. Si `numero < 3` → "reintentar" con `espera_tras(numero)`; si no → `marcar_con_error`, bitácora → "con error".

## Fuera de alcance

- El broker real (RabbitMQ), PostgreSQL y el almacenamiento institucional.
- Reprocesar actas "con error" (DT-01) y la alerta de más de 100 pendientes (R-04).
- Aprobar el acta (CU-08) y exportarla (CU-12).

## Ajuste ADR-011 (PDF real con ReportLab)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `aplicacion/actas/datos_acta.py` **(nuevo)** | `DatosActa` (DTO) | Datos consolidados del acta: `id_acta`, `id_practica`, `id_estudiante`, `id_empresa`, `id_tutor`, `plantilla`, `horas_aprobadas`, `horas_requeridas`, `calificaciones`, `observaciones`, `fecha_solicitud` |
| `aplicacion/errores/acta_no_componible.py` **(nuevo)** | `ActaNoComponible` | código `acta_no_componible`, mensaje "no se pudo componer el PDF del acta" |
| `aplicacion/puertos/componedor_acta.py` **(nuevo)** | `ComponedorActa` (Protocol) | `componer(datos: DatosActa) -> bytes`; lanza `ActaNoComponible` |
| `aplicacion/actas/generar_acta.py` **(cambia)** | `GenerarActa` | Recibe el `ComponedorActa`; `_consolidar` arma `DatosActa`; `ActaNoComponible` y `AlmacenNoDisponible` cuentan como intento fallido |
| `infraestructura/componedor_acta_reportlab.py` **(nuevo)** | `ComponedorActaReportlab` | `reportlab.pdfgen.canvas.Canvas` sobre `BytesIO`, carta, sin compresión de página; título, datos, horas, calificaciones, observaciones, plantilla y las tres líneas de aprobación electrónica (CU-08); cualquier excepción → `ActaNoComponible` |
| `src/worker.py` **(cambia)** | (composición del Worker) | Inyecta `ComponedorActaReportlab()` en `GenerarActa` |
| `src/requirements.txt` **(nuevo)** | — | `reportlab==5.1.0` |
