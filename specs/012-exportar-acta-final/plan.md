# Plan: 012 Exportar el acta final

Aterriza [spec.md](spec.md) (CU-12) en la arquitectura de [docs/arquitectura.md](../../docs/arquitectura.md). No agrega componentes fuera de las vistas y reutiliza lo construido en 001 a 011.

## Decisiones que aplican

| ID | Qué aplica a CU-12 |
|----|--------------------|
| ADR-001 | La API solo **lee** el PDF; nunca lo compone. `ExportarActa` no recibe el `ComponedorActa` (ADR-011), solo el `AlmacenActas`. |
| ADR-002 | El caso de uso vive en el **Módulo Actas** (`src/aplicacion/actas/`), que la vista de desarrollo asigna a CU-12. |
| ADR-003 | El PDF está en el Repositorio de actas (puerto `AlmacenActas`) y el acta guarda su ruta. |
| ADR-004 | El Coordinador exporta cualquier acta; el Estudiante solo la de su práctica. Autorización en el caso de uso. |
| ADR-006 | Se audita cada acceso rechazado; exportar no se audita. |
| ADR-007 | `ActaNoExportable` (409), `ActaNoEncontrada` (404) y `AlmacenNoDisponible` (503, la traduce el adaptador del almacén). |

## Componentes

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `src/aplicacion/errores/acta_no_exportable.py` **(nuevo)** | `ActaNoExportable` | código `acta_no_exportable`, mensaje "exportación no permitida", con `motivo` |
| `src/aplicacion/actas/solicitud_exportacion_acta.py` **(nuevo)** | `SolicitudExportacionActa` (DTO) | `usuario`, `id_acta` |
| `src/aplicacion/actas/acta_exportada.py` **(nuevo)** | `ActaExportada` (DTO) | `id_acta`, `nombre_archivo`, `tipo_contenido`, `contenido: bytes` |
| `src/aplicacion/actas/exportar_acta.py` **(nuevo)** | `ExportarActa` | Caso de uso (ver Flujo). Recibe repositorio, bitacora, `AlmacenActas` y reloj |
| `src/infraestructura/controlador_rest.py` **(cambia)** | `ControladorRest` | `exportar_acta(token, id_acta)` representa "GET /actas/{id}/pdf": 200 con `nombre_archivo`, `tipo_contenido` y `contenido` (bytes). Agrega 409 `ActaNoExportable` (con motivo) y 503 `AlmacenNoDisponible` |
| `src/main.py` **(cambia)** | (composición) | Crea `ExportarActa` con el `AlmacenActasMemoria` |

## Flujo

1. El controlador valida el token (401 si falla).
2. `ExportarActa.ejecutar(SolicitudExportacionActa)`:
   1. `obtener_acta`; si no existe → `ActaNoEncontrada`.
   2. Autoriza: rol `CoordinadorPracticas`, o rol `Estudiante` titular de la práctica del acta. Si no → bitácora (`acta:<id>`, "exportar acta") y `AccesoDenegado`.
   3. Estado distinto de "generada" y "aprobada", o sin ruta → `ActaNoExportable("el acta no tiene PDF generado")`.
   4. `almacen.leer(ruta)` (puede lanzar `AlmacenNoDisponible`) → `ActaExportada(id, "acta-<id>.pdf", "application/pdf", contenido)`.

## Fuera de alcance

- Firmar digitalmente el PDF (RN-01 descarta servicios pagos; las aprobaciones son internas, ADR-006).
- Exportar varias actas en un archivo comprimido.
