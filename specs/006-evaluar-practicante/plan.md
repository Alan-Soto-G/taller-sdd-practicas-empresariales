# Plan: 006 Evaluar el desempeño del practicante

Aterriza [spec.md](spec.md) (CU-06) en la arquitectura de [docs/arquitectura.md](../../docs/arquitectura.md). No agrega componentes fuera de [vistas/03-desarrollo.md](../../docs/vistas/03-desarrollo.md) y reutiliza lo construido en 001 a 005 sin cambiar su comportamiento.

## Decisiones que aplican

| ID | Qué aplica a CU-06 |
|----|--------------------|
| ADR-002 | Los casos de uso viven en el **Módulo Evaluación** (`src/aplicacion/evaluacion/`), que usa el **Módulo Configuración** para los criterios (vista de usos). Se agrega `ConsultarCriteriosEvaluacion` en `src/aplicacion/configuracion/`. |
| ADR-003 | RepositorioPracticas en memoria con representantes, enlaces y evaluaciones. Usar el enlace es atómico, para que no se use dos veces. |
| ADR-004 | El Coordinador emite el enlace con su token del SSO; la autorización por rol está en el caso de uso. |
| ADR-005 | El **Validador de enlace** (adaptador de entrada) valida el enlace y entrega una identidad acotada a una práctica y a una acción (`IdentidadEnlace`). El enlace vence a los 7 días, se invalida al usarse o al reemitirlo y no da acceso a otra acción. |
| ADR-006 | Se auditan el uso del enlace, la creación de la Evaluacion, el paso de la Práctica a "evaluada", cada acceso rechazado y cada intento con un enlace vencido, usado o inválido. ADR-006 dice que "los casos de uso escriben a través del puerto `Bitacora`": el Validador de enlace (adaptador) depende solo de RepositorioPracticas, como en la vista de desarrollo, y lanza `EnlaceNoValido` con el enlace y el representante; el controlador entrega ese intento al caso de uso `RegistrarEnlaceRechazado`, que lo audita (ajuste del 2026-11-20, tareas T-27 a T-33). |
| ADR-007 | Errores `EnlaceNoValido` (410), `EvaluacionNoPermitida` (409), `EvaluacionNoValida` (422) y `PracticaNoEncontrada` (404). Si el correo falla, el enlace no se revierte. |
| ADR-008 | Los criterios (`CriterioEvaluacion`) son datos de la ReglaPractica con la que empezó la Práctica. Agregar uno es agregar una versión de la regla (EAC-03). |
| Vista lógica | CriterioEvaluacion, RepresentanteEmpresa, EnlaceAcceso (acción, vencimiento, usado), Evaluacion (una por práctica, califica todos los criterios) y la transición "horas completas" → "evaluada". |
| Vista de desarrollo | Controlador REST, Validador de token, Validador de enlace, Módulo Evaluación, Módulo Configuración, puertos RepositorioPracticas, Notificador y Bitacora y sus adaptadores. |

## Componentes

Python 3.12, una clase por archivo, sin `__init__.py`. **(nuevo)** o **(cambia)**.

### dominio (`src/dominio/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `criterio_evaluacion.py` **(nuevo)** | `CriterioEvaluacion` | `nombre`, `escala` (se califica de 1 a `escala`) |
| `regla_practica.py` **(cambia)** | `ReglaPractica` | Agrega `criterios: tuple[CriterioEvaluacion, ...] = ()` al final, para no romper a quien la crea con cuatro argumentos |
| `representante_empresa.py` **(nuevo)** | `RepresentanteEmpresa` | `id`, `id_empresa`, `nombre`, `correo` |
| `enlace_acceso.py` **(nuevo)** | `EnlaceAcceso` | `id`, `token`, `id_practica`, `id_representante`, `accion`, `vence`, `usado=False`. `VIGENCIA_ENLACE = 7 días`. `emitir(...)` (classmethod). `motivo_rechazo(accion, ahora)`: "enlace inválido" si la acción no coincide, "enlace usado" si `usado`, "enlace vencido" si `ahora > vence`, o `None`. `usar()` devuelve una copia usada |
| `evaluacion.py` **(nuevo)** | `Evaluacion` | `id`, `id_practica`, `calificaciones: dict[str, int]`, `observaciones`, `fecha`. `motivo_invalidez(escalas, calificaciones)` (staticmethod), en este orden: el primer criterio sin calificar → "falta calificar el criterio X"; el primero fuera de 1..escala → "la calificación de X debe estar entre 1 y N"; el primero que no está en `escalas` → "criterio desconocido: X" |
| `practica.py` **(cambia)** | `Practica` | Agrega `evaluar()`: copia en `EVALUADA`; `ValueError` si no está en `HORAS_COMPLETAS` |

### aplicacion (`src/aplicacion/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `identidad_enlace.py` **(nuevo)** | `IdentidadEnlace` (DTO) | Lo entrega el Validador de enlace: `id_enlace`, `id_practica`, `id_representante`, `accion` |
| `errores/enlace_no_valido.py` **(nuevo)** | `EnlaceNoValido` | código `enlace_no_valido`, mensaje "enlace vencido: solicite uno nuevo a la Coordinación", con `motivo` |
| `errores/evaluacion_no_permitida.py` **(nuevo)** | `EvaluacionNoPermitida` | código `evaluacion_no_permitida`, mensaje "evaluación no permitida", con `motivo` |
| `errores/evaluacion_no_valida.py` **(nuevo)** | `EvaluacionNoValida` | código `evaluacion_no_valida`, mensaje "evaluación no válida", con `motivo` |
| `puertos/repositorio_practicas.py` **(cambia)** | `RepositorioPracticas` | Agrega `obtener_representante_de_empresa`, `guardar_enlace`, `obtener_enlace_por_token`, `invalidar_enlaces(id_practica, accion)`, `marcar_enlace_usado(id_enlace) -> bool` (atómico; `False` si ya estaba usado) y `guardar_evaluacion` |
| `configuracion/criterio_consultado.py` **(nuevo)** | `CriterioConsultado` (DTO) | `nombre`, `escala` |
| `configuracion/consultar_criterios_evaluacion.py` **(nuevo)** | `ConsultarCriteriosEvaluacion` | `ejecutar(version) -> tuple[CriterioConsultado, ...]` |
| `evaluacion/solicitud_enlace_evaluacion.py` **(nuevo)** | `SolicitudEnlaceEvaluacion` (DTO) | `usuario`, `id_practica` |
| `evaluacion/enlace_emitido.py` **(nuevo)** | `EnlaceEmitido` (DTO) | `id_enlace`, `id_practica`, `vence`, `correo_representante` |
| `evaluacion/emitir_enlace_evaluacion.py` **(nuevo)** | `EmitirEnlaceEvaluacion` | Paso 1 (ver Flujo). Recibe repositorio, bitacora, notificador y reloj |
| `evaluacion/formulario_evaluacion.py` **(nuevo)** | `FormularioEvaluacion` (DTO) | `id_practica`, `id_estudiante`, `criterios: tuple[CriterioConsultado, ...]` |
| `evaluacion/consultar_formulario_evaluacion.py` **(nuevo)** | `ConsultarFormularioEvaluacion` | Paso 2. Recibe repositorio y `ConsultarCriteriosEvaluacion` |
| `evaluacion/solicitud_evaluacion.py` **(nuevo)** | `SolicitudEvaluacion` (DTO) | `identidad: IdentidadEnlace`, `calificaciones: dict[str, int]`, `observaciones` |
| `evaluacion/evaluacion_registrada.py` **(nuevo)** | `EvaluacionRegistrada` (DTO) | `id`, `id_practica`, `estado_practica` |
| `evaluacion/registrar_evaluacion.py` **(nuevo)** | `RegistrarEvaluacion` | Paso 3. Recibe repositorio, bitacora, `ConsultarCriteriosEvaluacion` y reloj |

### infraestructura (`src/infraestructura/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `validador_enlace.py` **(nuevo)** | `ValidadorEnlace` | `validar(token, accion) -> IdentidadEnlace`. Recibe solo RepositorioPracticas y el reloj. Busca el enlace; si no existe o `motivo_rechazo` da un motivo, lanza `EnlaceNoValido(motivo, id_enlace, id_representante)`; no escribe en la bitácora (ADR-006) |
| `repositorio_practicas_memoria.py` **(cambia)** | `RepositorioPracticasMemoria` | Representantes, enlaces y evaluaciones; `agregar_representante`, `listar_enlaces`, `listar_evaluaciones`; `marcar_enlace_usado` dentro de un `Lock` |
| `controlador_rest.py` **(cambia)** | `ControladorRest` | Recibe `ValidadorEnlace`, `EmitirEnlaceEvaluacion`, `ConsultarFormularioEvaluacion` y `RegistrarEvaluacion`. `emitir_enlace_evaluacion(token, id_practica)` (POST /practicas/{id}/enlaces-evaluacion, 201), `abrir_evaluacion(enlace)` (GET /evaluaciones/{enlace}, 200) y `enviar_evaluacion(enlace, cuerpo)` (POST /evaluaciones/{enlace}, 201 "evaluación enviada"). Agrega 410, 409 y 422 de los errores nuevos, con su motivo |
| `aplicacion/evaluacion/intento_enlace_rechazado.py` **(nuevo, ajuste)** | `IntentoEnlaceRechazado` (DTO) | `id_enlace \| None`, `id_representante \| None`, `motivo` |
| `aplicacion/evaluacion/registrar_enlace_rechazado.py` **(nuevo, ajuste)** | `RegistrarEnlaceRechazado` | Caso de uso que audita el intento rechazado: usuario el representante o "desconocido", rol `RepresentanteEmpresa`, recurso `enlace:<id>` o `enlace:desconocido`, acción "usar enlace rechazado: <motivo>" (ADR-005, ADR-006) |
| `src/main.py` **(cambia)** | (composición) | Precarga los tres criterios en la regla "v1", el RepresentanteEmpresa "R-01" de "EMP-ACME", el Tutor "T-400", el Estudiante "E-1006" y la Practica "PR-06" ("horas completas", "T-400", "v1"); crea el Validador de enlace y los casos de uso |

Vista de usos: Módulo Evaluación → Módulo Configuración → dominio. Sin ciclos.

## Flujo

Secuencia [cu06-evaluar-practicante.puml](../../docs/diagramas/secuencias/cu06-evaluar-practicante.puml) (ESC-04):

1. **Emitir** (`EmitirEnlaceEvaluacion`):
   - rol distinto de Coordinador → bitácora (`practica:<id>`, "emitir enlace de evaluación") y `AccesoDenegado`;
   - la práctica no existe → `PracticaNoEncontrada`;
   - no está en "horas completas" → `EvaluacionNoPermitida("la práctica no tiene las horas completas")`;
   - no hay representante → `EvaluacionNoPermitida("la empresa no tiene representante registrado")`;
   - si todo va bien: `invalidar_enlaces(practica, "evaluar")`; `EnlaceAcceso.emitir` con id `EN-<8 hex>` y token `secrets.token_urlsafe(16)`; `guardar_enlace`; correo al representante con la ruta `/evaluaciones/<token>` (si lanza `CorreoNoEnviado`, se ignora); devuelve `EnlaceEmitido`.
2. **Abrir:** el controlador llama `ValidadorEnlace.validar(token, "evaluar")`; si lanza `EnlaceNoValido`, llama `RegistrarEnlaceRechazado` y responde 410 y `ConsultarFormularioEvaluacion` devuelve los criterios de `practica.version_regla`.
3. **Enviar:** el controlador valida el enlace igual que al abrir. `RegistrarEvaluacion`:
   - la práctica no está en "horas completas" → `EvaluacionNoPermitida("la práctica no está lista para evaluar")`;
   - `Evaluacion.motivo_invalidez` con las escalas de los criterios → `EvaluacionNoValida(motivo)`, sin consumir el enlace;
   - `marcar_enlace_usado` devuelve `False` → `EnlaceNoValido("enlace usado")`;
   - si todo va bien: guarda la Evaluacion con id `EV-<8 hex>`, pasa la Práctica a "evaluada" y audita el uso del enlace, la evaluación y el cambio de estado (usuario el representante, rol `RepresentanteEmpresa`).

## Fuera de alcance

- Gestionar empresas y representantes (CU-14) y administrar versiones de ReglaPractica desde la API (se precargan; EAC-03 se verifica agregando la regla como dato).
- Editar una evaluación enviada.
- La prueba de usuario de EAC-05 (menos de 5 minutos), la aplicación web móvil (ADR-010), el SMTP real y PostgreSQL.
