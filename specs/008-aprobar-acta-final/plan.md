# Plan: 008 Aprobar el acta final

Aterriza [spec.md](spec.md) (CU-08) en la arquitectura de [docs/arquitectura.md](../../docs/arquitectura.md). No agrega componentes fuera de [vistas/03-desarrollo.md](../../docs/vistas/03-desarrollo.md) y reutiliza lo construido en 001 a 007 sin cambiar su comportamiento.

## Decisiones que aplican

| ID | Qué aplica a CU-08 |
|----|--------------------|
| ADR-002 | Los casos de uso viven en el **Módulo Actas** (`src/aplicacion/actas/`), que según la vista de desarrollo cubre CU-07, CU-08 y CU-12. Reutiliza el DTO `EnlaceEmitido` del Módulo Evaluación: la vista de usos permite que Actas use Evaluación. |
| ADR-004 | Tutor (solo el asignado) y Coordinador aprueban con su token; la autorización por rol y titularidad está en el caso de uso. |
| ADR-005 | El Representante aprueba con un `EnlaceAcceso` de la acción "aprobar acta". Se reutiliza el `ValidadorEnlace` de CU-06, que rechaza y audita los enlaces de otra acción, usados o vencidos. Usar el enlace es atómico. |
| ADR-006 | La `Aprobacion` (rol, usuario y fecha) reemplaza la firma. Se auditan cada aprobación, el paso del acta a "aprobada", el de la Práctica a "cerrada" y cada acceso rechazado. |
| ADR-007 | `ActaNoEncontrada` (404) y `AprobacionNoPermitida` con motivo (409). Si falla el correo del enlace, el enlace no se revierte. |
| Vista lógica | Aprobacion (tres por acta), ActaFinal "generada" → "aprobada" y Práctica "acta en trámite" → "cerrada". |

## Componentes

Python 3.12, una clase por archivo, sin `__init__.py`. **(nuevo)** o **(cambia)**.

### dominio (`src/dominio/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `aprobacion.py` **(nuevo)** | `Aprobacion` | `id_acta`, `rol`, `usuario`, `fecha`. Constante `APROBACIONES_REQUERIDAS = 3` (tutor, empresa y coordinador) |
| `acta_final.py` **(cambia)** | `ActaFinal` | `aprobar()`: copia en `APROBADA`; `ValueError` si no está `GENERADA` |
| `practica.py` **(cambia)** | `Practica` | `cerrar()`: copia en `CERRADA`; `ValueError` si no está `ACTA_EN_TRAMITE` |

### aplicacion (`src/aplicacion/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `errores/acta_no_encontrada.py` **(nuevo)** | `ActaNoEncontrada` | código `acta_no_encontrada`, mensaje "acta no encontrada" |
| `errores/aprobacion_no_permitida.py` **(nuevo)** | `AprobacionNoPermitida` | código `aprobacion_no_permitida`, mensaje "aprobación no permitida", con `motivo` |
| `puertos/repositorio_practicas.py` **(cambia)** | `RepositorioPracticas` | Agrega `guardar_aprobacion`, `listar_aprobaciones(id_acta)` y `obtener_acta_de_practica(id_practica)` (la más reciente) |
| `actas/solicitud_enlace_aprobacion.py` **(nuevo)** | `SolicitudEnlaceAprobacion` (DTO) | `usuario`, `id_acta` |
| `actas/emitir_enlace_aprobacion.py` **(nuevo)** | `EmitirEnlaceAprobacion` | El Coordinador emite el enlace "aprobar acta" del acta generada (ver Flujo). Devuelve `EnlaceEmitido` |
| `actas/solicitud_aprobacion_acta.py` **(nuevo)** | `SolicitudAprobacionActa` (DTO) | `usuario`, `id_acta` |
| `actas/aprobacion_registrada.py` **(nuevo)** | `AprobacionRegistrada` (DTO) | `id_acta`, `rol`, `aprobaciones`, `estado_acta`, `estado_practica` |
| `actas/aprobar_acta.py` **(nuevo)** | `AprobarActa` | `aprobar_con_token(SolicitudAprobacionActa)` (Tutor o Coordinador) y `aprobar_con_enlace(IdentidadEnlace)` (Representante) |

### infraestructura (`src/infraestructura/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `repositorio_practicas_memoria.py` **(cambia)** | `RepositorioPracticasMemoria` | Aprobaciones y `obtener_acta_de_practica` |
| `controlador_rest.py` **(cambia)** | `ControladorRest` | `emitir_enlace_aprobacion(token, id_acta)` (POST /actas/{id}/enlaces-aprobacion, 201), `aprobar_acta(token, id_acta)` (POST /actas/{id}/aprobaciones, 201) y `aprobar_acta_con_enlace(enlace)` (POST /aprobaciones-acta/{enlace}, 201). 404 `ActaNoEncontrada` y 409 `AprobacionNoPermitida` con motivo |
| `src/main.py` **(cambia)** | (composición) | Precarga el Estudiante "E-1009", la Practica "PR-09" ("acta en trámite", "T-400"), su PDF en el almacén y el ActaFinal "AC-09" "generada" con esa ruta, y los tokens `tok-E-1009` |

## Flujo

1. **Emitir el enlace** (`EmitirEnlaceAprobacion`):
   - rol distinto de Coordinador → bitácora (`acta:<id>`, "emitir enlace de aprobación") y `AccesoDenegado`;
   - el acta no existe → `ActaNoEncontrada`;
   - no está "generada" → `AprobacionNoPermitida("el acta no está generada")`;
   - no hay representante → `AprobacionNoPermitida("la empresa no tiene representante registrado")`;
   - si todo va bien: `invalidar_enlaces(practica, "aprobar acta")`, emite y guarda el enlace, y lo envía por correo a `/aprobaciones-acta/<token>` (si falla el correo, se ignora).
2. **Aprobar con token** (`aprobar_con_token`):
   - el acta no existe → `ActaNoEncontrada` (antes de autorizar, porque la titularidad depende de la práctica del acta);
   - rol `Tutor` cuyo id no es el tutor de la práctica, o un rol distinto de `Tutor` y `CoordinadorPracticas` → bitácora (`acta:<id>`, "aprobar acta") y `AccesoDenegado`;
   - si está autorizado → `_registrar`.
3. **Aprobar con enlace** (`aprobar_con_enlace`): el controlador valida el enlace con `ValidadorEnlace.validar(token, "aprobar acta")`. Se busca el acta de la práctica; se valida `_puede_aprobar`; `marcar_enlace_usado` (si devuelve `False`, `EnlaceNoValido("enlace usado")`); se audita "usar enlace de aprobación" y se llama `_registrar` con rol `RepresentanteEmpresa`.
4. **`_registrar`:**
   - el acta no está "generada" → `AprobacionNoPermitida("el acta no está generada")`;
   - el rol ya aprobó → `AprobacionNoPermitida("el rol <rol> ya aprobó el acta")`;
   - si todo va bien: guarda la `Aprobacion` y audita "aprobar acta". Si ya hay 3: `acta.aprobar()`, `practica.cerrar()`, guarda ambos y audita los dos cambios de estado.

## Fuera de alcance

- Rechazar un acta o retirar una aprobación.
- Notificar al Estudiante del cierre (ningún documento lo pide para CU-08).
- Exportar el acta (CU-12).
