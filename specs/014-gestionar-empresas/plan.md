# Plan: 014 Gestionar empresas aliadas y sus representantes

Aterriza [spec.md](spec.md) (CU-14) en la arquitectura de [docs/arquitectura.md](../../docs/arquitectura.md). No agrega componentes fuera de [vistas/03-desarrollo.md](../../docs/vistas/03-desarrollo.md) y reutiliza lo construido en 001 a 013.

## Decisiones que aplican

| ID | Qué aplica a CU-14 |
|----|--------------------|
| ADR-002 | El caso de uso vive en el **Módulo Postulaciones** (`src/aplicacion/postulaciones/`), que la vista asigna a CU-01, CU-02 y CU-14. Un solo caso de uso `GestionarEmpresas` con una operación por acción del CRUD, como `AprobarActa` de CU-08. |
| ADR-004 | Solo `CoordinadorPracticas`; autorización en el caso de uso. |
| ADR-005 | El correo del representante es el destino de los enlaces (CU-06, CU-08). Actualizarlo hace que los enlaces nuevos lleguen al correo correcto (mitigación del riesgo de ADR-005 y de DT-04). |
| ADR-006 | Se audita el acceso rechazado. Empresa no tiene cambios de estado auditables (igual que la Plaza en CU-02). |
| ADR-007 | `EmpresaNoValida` (400, motivo), `EmpresaNoPermitida` (409, motivo) y `EmpresaNoEncontrada` (404, de CU-02). |

## Componentes

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `src/dominio/empresa.py` **(cambia)** | `Empresa` | Agrega `nit: str = ""` al final (las precargas de dos argumentos siguen valiendo) y `motivo_invalidez(razon_social, nit)`: razón social obligatoria; NIT con el formato `^\d{9}-\d$` |
| `src/dominio/representante_empresa.py` **(cambia)** | `RepresentanteEmpresa` | Agrega `motivo_invalidez(nombre, correo)`: nombre obligatorio; `Correo.es_valido` |
| `src/aplicacion/errores/empresa_no_valida.py` **(nuevo)** | `EmpresaNoValida` | código `empresa_no_valida`, mensaje "empresa no válida", con `motivo` |
| `src/aplicacion/errores/empresa_no_permitida.py` **(nuevo)** | `EmpresaNoPermitida` | código `empresa_no_permitida`, mensaje "empresa no permitida", con `motivo` |
| `src/aplicacion/puertos/repositorio_practicas.py` **(cambia)** | `RepositorioPracticas` | Agrega `listar_empresas`, `eliminar_empresa`, `listar_plazas` y `guardar_representante` |
| `src/aplicacion/postulaciones/solicitud_empresa.py` **(nuevo)** | `SolicitudEmpresa` (DTO) | `usuario`, `id_empresa`, `razon_social=""`, `nit=""` |
| `src/aplicacion/postulaciones/solicitud_representante.py` **(nuevo)** | `SolicitudRepresentante` (DTO) | `usuario`, `id_empresa`, `nombre`, `correo` |
| `src/aplicacion/postulaciones/empresa_gestionada.py` **(nuevo)** | `EmpresaGestionada` (DTO) | `id`, `razon_social`, `nit`, `id_representante`, `nombre_representante`, `correo_representante` (los tres últimos `None` si no hay) |
| `src/aplicacion/postulaciones/gestionar_empresas.py` **(nuevo)** | `GestionarEmpresas` | `crear`, `actualizar`, `eliminar`, `listar` y `registrar_representante` (ver Flujo) |
| `src/infraestructura/repositorio_practicas_memoria.py` **(cambia)** | `RepositorioPracticasMemoria` | Los cuatro métodos nuevos |
| `src/infraestructura/controlador_rest.py` **(cambia)** | `ControladorRest` | `crear_empresa` (POST /empresas, 201), `listar_empresas` (GET /empresas, 200), `actualizar_empresa` (PUT /empresas/{id}, 200), `eliminar_empresa` (DELETE /empresas/{id}, 204) y `registrar_representante` (PUT /empresas/{id}/representante, 200). 400 y 409 con motivo |
| `src/main.py` **(cambia)** | (composición) | Crea `GestionarEmpresas`; precarga el NIT de "EMP-ACME" |

## Flujo

Todas las operaciones empiezan validando el token (401) y el rol: si no es Coordinador → bitácora (`empresa:<id>` o `empresas`, "gestionar empresas") y `AccesoDenegado`.

- **crear:**
  - `Empresa.motivo_invalidez` → `EmpresaNoValida`;
  - id existente → `EmpresaNoPermitida("ya existe empresa <id>")`;
  - si todo va bien, `guardar_empresa`.
- **actualizar:**
  - no existe → `EmpresaNoEncontrada`;
  - `motivo_invalidez` → `EmpresaNoValida`;
  - si todo va bien, `guardar_empresa` con el mismo id.
- **eliminar:**
  - no existe → `EmpresaNoEncontrada`;
  - tiene plazas (`listar_plazas`) o prácticas (`listar_practicas`) → `EmpresaNoPermitida("la empresa tiene plazas o prácticas")`;
  - si todo va bien, `eliminar_empresa`.
- **listar:** todas las empresas ordenadas por id, con su representante.
- **registrar_representante:**
  - la empresa no existe → `EmpresaNoEncontrada`;
  - `RepresentanteEmpresa.motivo_invalidez` → `EmpresaNoValida`;
  - si todo va bien, conserva el id del representante actual o crea `R-<8 hex>`, y llama `guardar_representante`.

## Fuera de alcance

- Gestionar convenios y varios representantes por empresa.
- Reemitir automáticamente los enlaces al cambiar el correo (lo decide el Coordinador, ADR-005).
