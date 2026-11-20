# Plan: 010 Consultar el estado de la práctica y del acta

Aterriza [spec.md](spec.md) (CU-10) en la arquitectura de [docs/arquitectura.md](../../docs/arquitectura.md). No agrega componentes fuera de [vistas/03-desarrollo.md](../../docs/vistas/03-desarrollo.md) y reutiliza lo construido en 001 a 009 sin cambiar su comportamiento.

## Decisiones que aplican

| ID | Qué aplica a CU-10 |
|----|--------------------|
| ADR-002 | El caso de uso vive en el **Módulo Seguimiento**. Usa en solo lectura el Módulo Horas (`ResumirHorasPractica`, de CU-09) y el Módulo Actas: se agrega `ConsultarActaPractica` en `src/aplicacion/actas/`. Sin ciclos: Actas no usa Seguimiento. |
| ADR-004 | Solo el rol `Estudiante`, y solo el titular de la práctica. La autorización está en el caso de uso. |
| ADR-006 | Se audita cada acceso rechazado (EAC-04). Las consultas no se auditan. |
| ADR-007 | `PracticaNoEncontrada` (404) y `AccesoDenegado` (403). |
| ADR-008 | Las horas requeridas salen de la versión de la práctica (a través de `ResumirHorasPractica`). |

## Componentes

Python 3.12, una clase por archivo, sin `__init__.py`. **(nuevo)** o **(cambia)**.

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `src/aplicacion/puertos/repositorio_practicas.py` **(cambia)** | `RepositorioPracticas` | Agrega `listar_practicas_de_estudiante(id_estudiante) -> list[Practica]` (ordenadas por id) |
| `src/aplicacion/actas/resumen_acta.py` **(nuevo)** | `ResumenActa` (DTO) | `id_acta`, `estado`, `aprobaciones` |
| `src/aplicacion/actas/consultar_acta_practica.py` **(nuevo)** | `ConsultarActaPractica` | Módulo Actas, solo lectura: `ejecutar(id_practica) -> ResumenActa \| None` (el acta más reciente y su número de aprobaciones) |
| `src/aplicacion/seguimiento/solicitud_estado_practica.py` **(nuevo)** | `SolicitudEstadoPractica` (DTO) | `usuario`, `id_practica: str \| None` |
| `src/aplicacion/seguimiento/estado_practica_consultado.py` **(nuevo)** | `EstadoPracticaConsultado` (DTO) | `id_practica`, `id_empresa`, `id_tutor`, `estado`, `horas_aprobadas`, `horas_requeridas`, `horas_pendientes`, `porcentaje`, `evaluacion_registrada`, `acta: ResumenActa \| None` |
| `src/aplicacion/seguimiento/estado_practicas_estudiante.py` **(nuevo)** | `EstadoPracticasEstudiante` (DTO) | `id_estudiante`, `practicas` |
| `src/aplicacion/seguimiento/consultar_estado_practica.py` **(nuevo)** | `ConsultarEstadoPractica` | Caso de uso (ver Flujo). Recibe repositorio, bitacora, `ResumirHorasPractica`, `ConsultarActaPractica` y reloj |
| `src/infraestructura/repositorio_practicas_memoria.py` **(cambia)** | `RepositorioPracticasMemoria` | `listar_practicas_de_estudiante` |
| `src/infraestructura/controlador_rest.py` **(cambia)** | `ControladorRest` | `consultar_estado(token, id_practica=None)`: representa "GET /estudiantes/yo/practicas" y "GET /practicas/{id}/estado"; 200 |
| `src/main.py` **(cambia)** | (composición) | Crea `ConsultarActaPractica` y `ConsultarEstadoPractica`; agrega el token `tok-E-1008` |

## Flujo

1. El controlador valida el token (401 si falla).
2. `ConsultarEstadoPractica.ejecutar`:
   1. Rol distinto de `Estudiante` → bitácora (recurso `practica:<id>` o `practicas:estudiante`, acción "consultar estado") y `AccesoDenegado`.
   2. Con `id_practica`: si no existe → `PracticaNoEncontrada`; si `id_estudiante` no es el usuario → bitácora y `AccesoDenegado` (EAC-04).
   3. Sin `id_practica`: `listar_practicas_de_estudiante`.
   4. Por cada práctica arma `EstadoPracticaConsultado` con:
      - el resumen de horas de `ResumirHorasPractica`;
      - si hay evaluación (`obtener_evaluacion_de_practica is not None`);
      - el acta que devuelve `ConsultarActaPractica`.

## Fuera de alcance

- Ver las calificaciones de la evaluación o descargar el acta (CU-12).
- Notificaciones de cambios de estado.
