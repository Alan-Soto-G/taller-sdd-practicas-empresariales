# Plan: 009 Consultar el avance de los estudiantes asignados

Aterriza [spec.md](spec.md) (CU-09) en la arquitectura de [docs/arquitectura.md](../../docs/arquitectura.md). No agrega componentes fuera de [vistas/03-desarrollo.md](../../docs/vistas/03-desarrollo.md) y reutiliza lo construido en 001 a 008 sin cambiar su comportamiento.

## Decisiones que aplican

| ID | Qué aplica a CU-09 |
|----|--------------------|
| ADR-002 | El caso de uso vive en el **Módulo Seguimiento** (`src/aplicacion/seguimiento/`). Según la vista de usos, Seguimiento usa en solo lectura el Módulo Horas: se agrega en el Módulo Horas `ResumirHorasPractica`, que a su vez usa el Módulo Configuración (`ConsultarHorasRequeridas`, de CU-05). Así Seguimiento no depende directamente de Configuración. |
| ADR-004 | Solo el rol `Tutor`, y para una práctica concreta solo su tutor asignado. La autorización está en el caso de uso. |
| ADR-006 | Se audita cada acceso rechazado. Las consultas exitosas no cambian estado y no se auditan. |
| ADR-007 | `PracticaNoEncontrada` (404) y `AccesoDenegado` (403) con la respuesta unificada. |
| ADR-008 | Las horas requeridas salen de la versión de ReglaPractica de cada práctica. |

## Componentes

Python 3.12, una clase por archivo, sin `__init__.py`. **(nuevo)** o **(cambia)**.

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `src/aplicacion/puertos/repositorio_practicas.py` **(cambia)** | `RepositorioPracticas` | Agrega `listar_practicas_de_tutor(id_tutor) -> list[Practica]` (ordenadas por id) y `listar_registros_horas_de_practica(id_practica) -> list[RegistroHoras]` |
| `src/aplicacion/horas/resumen_horas.py` **(nuevo)** | `ResumenHoras` (DTO) | `horas_aprobadas`, `horas_requeridas`, `horas_pendientes`, `porcentaje` |
| `src/aplicacion/horas/resumir_horas_practica.py` **(nuevo)** | `ResumirHorasPractica` | Módulo Horas, solo lectura: `ejecutar(id_practica, version_regla) -> ResumenHoras`. Aprobadas y pendientes (reportadas) de los registros; requeridas con `ConsultarHorasRequeridas`; porcentaje `min(100, aprobadas * 100 // requeridas)` |
| `src/aplicacion/seguimiento/solicitud_avance_tutor.py` **(nuevo)** | `SolicitudAvanceTutor` (DTO) | `usuario`, `id_practica: str \| None` |
| `src/aplicacion/seguimiento/avance_practica.py` **(nuevo)** | `AvancePractica` (DTO) | `id_practica`, `id_estudiante`, `estado`, `horas_aprobadas`, `horas_requeridas`, `horas_pendientes`, `porcentaje` |
| `src/aplicacion/seguimiento/avance_tutor.py` **(nuevo)** | `AvanceTutor` (DTO) | `id_tutor`, `practicas: tuple[AvancePractica, ...]` |
| `src/aplicacion/seguimiento/consultar_avance_tutor.py` **(nuevo)** | `ConsultarAvanceTutor` | Caso de uso (ver Flujo). Recibe repositorio, bitacora, `ResumirHorasPractica` y reloj |
| `src/infraestructura/repositorio_practicas_memoria.py` **(cambia)** | `RepositorioPracticasMemoria` | Los dos métodos nuevos |
| `src/infraestructura/controlador_rest.py` **(cambia)** | `ControladorRest` | `consultar_avance(token, id_practica=None)`: representa "GET /tutores/yo/avance" y "GET /practicas/{id}/avance"; 200 con `id_tutor` y la lista `practicas` |
| `src/main.py` **(cambia)** | (composición) | Crea `ResumirHorasPractica` y `ConsultarAvanceTutor`. Precarga el Tutor "T-500", los Estudiantes "E-1010" y "E-1011", las Practicas "PR-10" y "PR-11" ("en curso", "T-500", "v1"), 3 registros aprobados y 1 reportado de "PR-10", y los tokens `tok-T-500` y `tok-E-1010` |

Vista de usos: Seguimiento → Horas → Configuración → dominio. Sin ciclos.

## Flujo

1. El controlador valida el token (401 si falla).
2. `ConsultarAvanceTutor.ejecutar(SolicitudAvanceTutor)`:
   1. Rol distinto de `Tutor` → bitácora (recurso `practica:<id>` o `practicas:tutor`, acción "consultar avance") y `AccesoDenegado`.
   2. Con `id_practica`: si no existe → `PracticaNoEncontrada`; si `id_tutor` no es el usuario → bitácora y `AccesoDenegado`; si no, la lista es esa práctica.
   3. Sin `id_practica`: `listar_practicas_de_tutor(usuario.id)`.
   4. Por cada práctica, `ResumirHorasPractica.ejecutar(id, version_regla)` → `AvancePractica`.
   5. Devuelve `AvanceTutor`.

## Fuera de alcance

- Consultas del Coordinador (CU-11) y del Estudiante (CU-10).
- Filtros, paginación y exportación del avance.
