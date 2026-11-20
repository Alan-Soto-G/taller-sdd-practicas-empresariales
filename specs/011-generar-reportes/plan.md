# Plan: 011 Generar reportes de prácticas

Aterriza [spec.md](spec.md) (CU-11) en la arquitectura de [docs/arquitectura.md](../../docs/arquitectura.md). No agrega componentes fuera de [vistas/03-desarrollo.md](../../docs/vistas/03-desarrollo.md) y reutiliza lo construido en 001 a 010.

## Decisiones que aplican

| ID | Qué aplica a CU-11 |
|----|--------------------|
| ADR-002 | El caso de uso vive en el **Módulo Seguimiento**. Usa en solo lectura el Módulo Horas (`ResumirHorasPractica`) y el Módulo Actas (`ConsultarActaPractica`), los dos de CU-09 y CU-10. No necesita casos de uso nuevos en otros módulos. |
| ADR-004 | Solo el rol `CoordinadorPracticas`; la autorización está en el caso de uso. |
| ADR-006 | Se audita el acceso rechazado; generar el reporte no se audita. |
| ADR-007 | `EmpresaNoEncontrada` (404) y `AccesoDenegado` (403). |
| Sin librerías | El reporte es JSON (estructuras de Python en el controlador). Exportarlo a Excel o PDF necesitaría un ADR nuevo. |

## Componentes

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `src/aplicacion/puertos/repositorio_practicas.py` **(cambia)** | `RepositorioPracticas` | Agrega `listar_practicas() -> list[Practica]`, que el adaptador en memoria ya tiene desde CU-03 |
| `src/aplicacion/seguimiento/solicitud_reporte.py` **(nuevo)** | `SolicitudReporte` (DTO) | `usuario`, `id_empresa: str \| None` |
| `src/aplicacion/seguimiento/reporte_practicas.py` **(nuevo)** | `ReportePracticas` (DTO) | `id_empresa`, `total_practicas`, `por_estado`, `por_empresa`, `por_tutor`, `actas_por_estado`, `horas_aprobadas`, `generado` |
| `src/aplicacion/seguimiento/generar_reporte.py` **(nuevo)** | `GenerarReporte` | Caso de uso (ver Flujo). Recibe repositorio, bitacora, `ResumirHorasPractica`, `ConsultarActaPractica` y reloj |
| `src/infraestructura/controlador_rest.py` **(cambia)** | `ControladorRest` | `generar_reporte(token, id_empresa=None)`: representa "GET /reportes/practicas"; 200 con el reporte |
| `src/main.py` **(cambia)** | (composición) | Crea `GenerarReporte` |

## Flujo

1. El controlador valida el token (401 si falla).
2. `GenerarReporte.ejecutar(SolicitudReporte)`:
   1. Rol distinto de Coordinador → bitácora (`reportes`, "generar reporte") y `AccesoDenegado`.
   2. Con `id_empresa`: si `obtener_empresa` da `None` → `EmpresaNoEncontrada`.
   3. Toma `listar_practicas()` (filtradas por empresa si se indicó) y cuenta:
      - por estado: los 6 valores de `EstadoPractica`, en orden;
      - por empresa y por tutor ("sin tutor" si no tiene);
      - por estado del acta: "sin acta" y los 4 de `EstadoActa`, con `ConsultarActaPractica`;
      - la suma de horas aprobadas, con `ResumirHorasPractica`.
   4. Devuelve `ReportePracticas` con la hora de generación.

## Fuera de alcance

- Exportar el reporte a Excel o PDF, reportes históricos guardados y filtros por fecha o periodo (la Práctica no guarda periodo).
