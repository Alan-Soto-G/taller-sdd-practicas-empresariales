# Plan: 004 Registrar horas de práctica

Aterriza [spec.md](spec.md) (CU-04) en la arquitectura de [docs/arquitectura.md](../../docs/arquitectura.md). No agrega componentes fuera de [vistas/03-desarrollo.md](../../docs/vistas/03-desarrollo.md) y reutiliza lo construido en 001 a 003 sin cambiar su comportamiento.

## Decisiones que aplican

| ID | Qué aplica a CU-04 |
|----|--------------------|
| ADR-001 | La API no genera actas: el registro de horas solo valida y guarda, sin trabajos pesados (EAC-01). |
| ADR-002 | El caso de uso vive en el **Módulo Horas** (`src/aplicacion/horas/`). CU-04 no necesita las horas requeridas, así que todavía no usa el Módulo Configuración. |
| ADR-003 | RepositorioPracticas en memoria. La regla "un solo registro por práctica y semana" se garantiza en el adaptador con una operación atómica (equivale a la restricción única de PostgreSQL), para que dos peticiones simultáneas no dupliquen el registro (EAC-01). |
| ADR-004 | Autorización por rol (`Estudiante`) y por **titularidad** (la Practica pertenece al usuario) en el caso de uso. |
| ADR-006 | Se audita la creación del RegistroHoras ("crear con estado reportado") y cada acceso rechazado (rol o titularidad), con usuario, rol, recurso, acción y hora. |
| ADR-007 | Errores `PracticaNoEncontrada` (404) y `RegistroNoValido` con motivo (422, como en la secuencia). Respuesta unificada en el controlador. |
| Vista lógica | RegistroHoras (semana, horas, actividades, estado), EstadoRegistroHoras (reportado, aprobado, rechazado), Practica "en curso". |
| Vista de desarrollo | Controlador REST, Validador de token, Módulo Horas, puertos RepositorioPracticas y Bitacora y sus adaptadores en memoria. |

## Componentes

Python 3.12, una clase por archivo, sin `__init__.py`. **(nuevo)** o **(cambia)**.

### dominio (`src/dominio/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `estado_registro_horas.py` **(nuevo)** | `EstadoRegistroHoras` (StrEnum) | `REPORTADO="reportado"`, `APROBADO="aprobado"`, `RECHAZADO="rechazado"` |
| `registro_horas.py` **(nuevo)** | `RegistroHoras` (dataclass frozen) | `id`, `id_practica`, `semana`, `horas`, `actividades`, `fecha: date`, `estado`. `reportar(...)` (classmethod) crea uno en estado `REPORTADO`. `motivo_invalidez(semana, horas, actividades) -> str \| None` (staticmethod), en este orden: semana fuera de `^\d{4}-W(0[1-9]\|[1-4]\d\|5[0-3])$` → "la semana debe tener el formato AAAA-Wss (semana 01 a 53)"; horas fuera de 1..168 → "las horas deben estar entre 1 y 168"; actividades vacías o en blanco → "las actividades son obligatorias" |

### aplicacion (`src/aplicacion/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `errores/practica_no_encontrada.py` **(nuevo)** | `PracticaNoEncontrada` | código `practica_no_encontrada`, mensaje "práctica no encontrada" |
| `errores/registro_no_valido.py` **(nuevo)** | `RegistroNoValido` | código `registro_no_valido`, mensaje "registro no válido", con `motivo` |
| `puertos/repositorio_practicas.py` **(cambia)** | `RepositorioPracticas` | Agrega `existe_registro_horas(id_practica, semana) -> bool` y `guardar_registro_horas(registro) -> bool` (guarda de forma atómica y devuelve `False`, sin guardar, si ya hay un registro de esa práctica y semana) |
| `horas/solicitud_registro_horas.py` **(nuevo)** | `SolicitudRegistroHoras` (DTO de entrada) | `usuario`, `id_practica`, `semana`, `horas`, `actividades` |
| `horas/horas_reportadas.py` **(nuevo)** | `HorasReportadas` (DTO de salida) | `id`, `id_practica`, `semana`, `horas`, `estado`, `fecha` |
| `horas/registrar_horas.py` **(nuevo)** | `RegistrarHoras` | Caso de uso de CU-04 (ver Flujo). Recibe `RepositorioPracticas`, `Bitacora` y `reloj` |

### infraestructura (`src/infraestructura/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `repositorio_practicas_memoria.py` **(cambia)** | `RepositorioPracticasMemoria` | Lista de registros de horas protegida con un `threading.Lock`; `existe_registro_horas`, `guardar_registro_horas` (comprueba y agrega dentro del lock) y `listar_registros_horas()` |
| `controlador_rest.py` **(cambia)** | `ControladorRest` | Recibe también `RegistrarHoras`. `registrar_horas(token, id_practica, cuerpo)` representa "POST /practicas/{id}/horas": cuerpo `semana`, `horas`, `actividades`; 201 con el DTO y el mensaje "horas reportadas, pendientes de aprobación del tutor". Agrega 404 `PracticaNoEncontrada` y 422 `RegistroNoValido` (con motivo) |
| `src/main.py` **(cambia)** | (composición) | Crea `RegistrarHoras`. Precarga el Estudiante "E-1004", la Practica "PR-04" ("en curso" con "T-300", regla "v1") y los tokens `tok-E-1004` (Estudiante) y `tok-T-300` (Tutor) |

## Flujo

Secuencia [cu04-registrar-horas.puml](../../docs/diagramas/secuencias/cu04-registrar-horas.puml) (ESC-03):

1. `ControladorRest.registrar_horas` recibe "POST /practicas/{id}/horas"; el `ValidadorToken` valida el token (401 si falla).
2. `RegistrarHoras.ejecutar(SolicitudRegistroHoras)`:
   1. Rol distinto de `Estudiante` → bitácora (recurso `practica:<id>`, acción "registrar horas") y `AccesoDenegado`.
   2. `obtener_practica`; si no existe → `PracticaNoEncontrada`.
   3. `practica.id_estudiante != usuario.id` → bitácora del acceso ajeno (mismo formato) y `AccesoDenegado` (EAC-04).
   4. `practica.estado != EN_CURSO` → `RegistroNoValido("la práctica no está en curso")`.
   5. `RegistroHoras.motivo_invalidez(...)` → `RegistroNoValido(motivo)`.
   6. `existe_registro_horas` → `RegistroNoValido("la semana ya tiene un registro")`.
   7. Crea el registro con id `RH-<8 hex>` y `guardar_registro_horas`; si devuelve `False` (otra petición ganó la carrera) → `RegistroNoValido("la semana ya tiene un registro")`.
   8. Bitácora (recurso `registro_horas:<id>`, acción "crear con estado reportado") y devuelve `HorasReportadas`.
3. El controlador responde 201 o traduce el error.

## Fuera de alcance

- Aprobar o rechazar horas (CU-05), corregir o borrar un registro.
- Pasar la Práctica a "horas completas" (depende de horas aprobadas, CU-05).
- La prueba de carga real sobre PostgreSQL y réplicas (R-02, ADR-009): EAC-01 se mide aquí con la composición en memoria.
- Servidor HTTP real, aplicación web y pruebas automatizadas.
