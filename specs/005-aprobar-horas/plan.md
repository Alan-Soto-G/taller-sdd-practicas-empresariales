# Plan: 005 Aprobar horas reportadas

Aterriza [spec.md](spec.md) (CU-05) en la arquitectura de [docs/arquitectura.md](../../docs/arquitectura.md). No agrega componentes fuera de [vistas/03-desarrollo.md](../../docs/vistas/03-desarrollo.md) y reutiliza lo construido en 001 a 004 sin cambiar su comportamiento.

## Decisiones que aplican

| ID | Qué aplica a CU-05 |
|----|--------------------|
| ADR-002 | El caso de uso vive en el **Módulo Horas** (`src/aplicacion/horas/`), que según la vista de usos usa el **Módulo Configuración** para las horas requeridas: se agrega `ConsultarHorasRequeridas` en `src/aplicacion/configuracion/`. |
| ADR-003 | RepositorioPracticas en memoria con los métodos nuevos. |
| ADR-004 | Autorización en el caso de uso: rol `Tutor` y titularidad (el Tutor asignado a la Práctica del registro). Cualquier otro usuario recibe `AccesoDenegado`. |
| ADR-006 | Se audita el cambio de estado del RegistroHoras (la aprobación electrónica), el cambio de estado de la Práctica a "horas completas" y cada acceso rechazado. |
| ADR-007 | `RegistroNoEncontrado` (404) y `RegistroNoValido` con motivo (422, de CU-04). Respuesta unificada en el controlador. |
| ADR-008 | Las horas requeridas salen de la versión de ReglaPractica de la Práctica (`version_regla`), no de la vigente. |
| Vista lógica | RegistroHoras (estados; "aprobado no se modifica"), Practica (transición "en curso" → "horas completas"), ReglaPractica (horas requeridas). |
| Vista de desarrollo | Controlador REST, Validador de token, Módulo Horas, Módulo Configuración, puertos RepositorioPracticas y Bitacora y sus adaptadores en memoria. |

## Componentes

Python 3.12, una clase por archivo, sin `__init__.py`. **(nuevo)** o **(cambia)**.

### dominio (`src/dominio/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `registro_horas.py` **(cambia)** | `RegistroHoras` | Agrega `aprobar() -> RegistroHoras` y `rechazar() -> RegistroHoras`: copia con el estado nuevo; lanzan `ValueError` si el estado no es `REPORTADO` (regla "aprobado no se modifica") |
| `practica.py` **(cambia)** | `Practica` | Agrega `completar_horas() -> Practica`: copia en `HORAS_COMPLETAS`; lanza `ValueError` si el estado no es `EN_CURSO` |

### aplicacion (`src/aplicacion/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `errores/registro_no_encontrado.py` **(nuevo)** | `RegistroNoEncontrado` | código `registro_no_encontrado`, mensaje "registro de horas no encontrado" |
| `puertos/repositorio_practicas.py` **(cambia)** | `RepositorioPracticas` | Agrega `obtener_regla(version) -> ReglaPractica \| None`, `obtener_registro_horas(id) -> RegistroHoras \| None`, `actualizar_registro_horas(registro) -> None` y `sumar_horas_aprobadas(id_practica) -> int` |
| `configuracion/consultar_horas_requeridas.py` **(nuevo)** | `ConsultarHorasRequeridas` | Módulo Configuración: `ejecutar(version) -> int` con las horas requeridas de esa versión de ReglaPractica |
| `horas/solicitud_revision_horas.py` **(nuevo)** | `SolicitudRevisionHoras` (DTO de entrada) | `usuario`, `id_registro`, `decision` ("aprobar" o "rechazar") |
| `horas/horas_revisadas.py` **(nuevo)** | `HorasRevisadas` (DTO de salida) | `id`, `id_practica`, `estado`, `horas_aprobadas`, `estado_practica` |
| `horas/aprobar_horas.py` **(nuevo)** | `AprobarHoras` | Caso de uso de CU-05 (ver Flujo). Recibe `RepositorioPracticas`, `Bitacora`, `ConsultarHorasRequeridas` y `reloj` |

### infraestructura (`src/infraestructura/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `repositorio_practicas_memoria.py` **(cambia)** | `RepositorioPracticasMemoria` | `obtener_regla`, `obtener_registro_horas`, `actualizar_registro_horas` (reemplaza por id dentro del lock) y `sumar_horas_aprobadas` |
| `controlador_rest.py` **(cambia)** | `ControladorRest` | Recibe también `AprobarHoras`. `revisar_horas(token, id_registro, cuerpo)` representa "POST /registros-horas/{id}/revision" con el cuerpo `decision`; 200 con el DTO y el mensaje "horas aprobadas" u "horas rechazadas". Agrega 404 `RegistroNoEncontrado` |
| `src/main.py` **(cambia)** | (composición) | Crea `ConsultarHorasRequeridas` y `AprobarHoras`. Precarga el Estudiante "E-1005", la Practica "PR-05" ("en curso", "T-300", "v1") y el RegistroHoras "RH-05" (semana "2026-W46", 20 horas, "reportado"), y el token `tok-E-1005` |

Vista de usos: Módulo Horas → Módulo Configuración → dominio. Sin ciclos.

## Flujo

CU-05 no es primario: no tiene diagrama propio. Sigue la forma de [cu04-registrar-horas.puml](../../docs/diagramas/secuencias/cu04-registrar-horas.puml).

1. `ControladorRest.revisar_horas` valida el token (401 si falla).
2. `AprobarHoras.ejecutar(SolicitudRevisionHoras)`:
   1. Rol distinto de `Tutor` → bitácora (recurso `registro_horas:<id>`, acción "aprobar horas") y `AccesoDenegado`.
   2. `obtener_registro_horas`; si no existe → `RegistroNoEncontrado`.
   3. `obtener_practica(registro.id_practica)`; si `practica.id_tutor != usuario.id` → bitácora (mismo formato) y `AccesoDenegado` (EAC-04).
   4. Decisión distinta de "aprobar" y "rechazar" → `RegistroNoValido("la decisión debe ser aprobar o rechazar")`.
   5. Estado distinto de "reportado" → `RegistroNoValido("el registro ya fue revisado")`.
   6. `registro.aprobar()` o `registro.rechazar()`, `actualizar_registro_horas` y bitácora (recurso `registro_horas:<id>`, acción "cambiar estado de reportado a aprobado/rechazado").
   7. `horas = sumar_horas_aprobadas(practica.id)`. Si se aprobó, la práctica está "en curso" y `horas >= ConsultarHorasRequeridas.ejecutar(practica.version_regla)`: `practica.completar_horas()`, `guardar_practica` y bitácora (recurso `practica:<id>`, acción "cambiar estado de en curso a horas completas").
   8. Devuelve `HorasRevisadas`.
3. El controlador responde 200 o traduce el error.

## Fuera de alcance

- Observaciones del rechazo, corregir un registro rechazado y aprobar varios registros a la vez.
- Notificar al Estudiante (ningún documento lo pide para CU-05).
- Servidor HTTP real, PostgreSQL, aplicación web y pruebas automatizadas.
