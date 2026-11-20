# Plan: 002 Publicar plazas de práctica

Aterriza [spec.md](spec.md) (CU-02) en la arquitectura de [docs/arquitectura.md](../../docs/arquitectura.md). No agrega componentes fuera de [vistas/03-desarrollo.md](../../docs/vistas/03-desarrollo.md) y reutiliza lo construido en [001](../001-postularse-plaza-practica/plan.md) sin cambiar su comportamiento.

## Decisiones que aplican

| ID | Qué aplica a CU-02 |
|----|--------------------|
| ADR-002 | El caso de uso vive en el Módulo Postulaciones, que según la vista de desarrollo cubre CU-01, CU-02 y CU-14. Capas `dominio/`, `aplicacion/` e `infraestructura/` bajo `src/`. `dominio/` no importa nada de las otras capas. Los puertos son `Protocol` en `aplicacion/puertos/`. |
| ADR-003 | El Adaptador PostgreSQL implementa RepositorioPracticas. En esta etapa se amplía el adaptador en memoria de CU-01 con el mismo puerto (`AGENTS.md`). |
| ADR-004 | El Validador de token de CU-01 valida el token de 15 minutos y entrega la identidad y el rol. La autorización por rol (solo `CoordinadorPracticas` publica) se hace **en el caso de uso**, no en el controlador. |
| ADR-006 | El caso de uso registra en la `Bitacora` cada acceso rechazado, con usuario, rol, recurso, acción y hora. Publicar una Plaza no se audita: la Plaza no está entre las entidades con cambios de estado que lista el ADR (decisión de la spec). Los rechazos por validación tampoco se auditan, igual que en CU-01. |
| ADR-007 | El caso de uso lanza errores de aplicación propios, que heredan de `ErrorAplicacion`. El Controlador REST los convierte en la respuesta unificada (código, mensaje, motivo si lo hay e identificador de correlación). |
| ADR-008 | No aplica: CU-02 no usa ReglaPractica. |
| Vista lógica (01-logica.md) | Empresa (aliada con convenio vigente) y Plaza (cargo, cupos, periodo). La regla "no más aceptadas que cupos" de CU-01 no cambia. |
| Vista de desarrollo (03-desarrollo.md) | Controlador REST, Validador de token, Módulo Postulaciones, puertos RepositorioPracticas y Bitacora, sus adaptadores en memoria y `main.py` como composición. |

## Componentes

Python 3.12, una clase por archivo, sin `__init__.py`, nombres del glosario. Se marca con **(nuevo)** o **(cambia)** cada archivo.

### dominio (`src/dominio/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `src/dominio/empresa.py` **(nuevo)** | `Empresa` | id y razón social. Toda Empresa registrada es aliada con convenio vigente (spec); no se valida el convenio. El NIT de la vista lógica se agrega con CU-14 |
| `src/dominio/plaza.py` **(cambia)** | `Plaza` | Conserva `tiene_cupo`. Agrega `Plaza.motivo_invalidez(cargo, cupos, periodo) -> str \| None` (método estático): devuelve "el cargo es obligatorio" si el cargo está vacío o en blanco, "los cupos deben ser mayores que cero" si `cupos <= 0` y "el periodo debe tener el formato AAAA-1 o AAAA-2" si el periodo no cumple `^\d{4}-[12]$`; `None` si los datos son válidos. Se revisan en ese orden |

### aplicacion (`src/aplicacion/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `src/aplicacion/puertos/repositorio_practicas.py` **(cambia)** | `RepositorioPracticas` (Protocol) | Conserva los métodos de CU-01. Agrega `obtener_empresa(id_empresa) -> Empresa \| None` y `guardar_plaza(plaza) -> None` |
| `src/aplicacion/errores/empresa_no_encontrada.py` **(nuevo)** | `EmpresaNoEncontrada` | Código `empresa_no_encontrada`, mensaje "empresa no encontrada" |
| `src/aplicacion/errores/plaza_no_valida.py` **(nuevo)** | `PlazaNoValida` | Código `plaza_no_valida`, mensaje "plaza no válida"; lleva el `motivo` (igual que `PostulacionNoPermitida`) |
| `src/aplicacion/postulaciones/solicitud_publicacion_plaza.py` **(nuevo)** | `SolicitudPublicacionPlaza` (DTO de entrada) | usuario autenticado, id de la empresa, cargo, cupos y periodo |
| `src/aplicacion/postulaciones/plaza_publicada.py` **(nuevo)** | `PlazaPublicada` (DTO de salida) | id de la plaza, id de la empresa, cargo, cupos y periodo |
| `src/aplicacion/postulaciones/publicar_plaza.py` **(nuevo)** | `PublicarPlaza` | Caso de uso de CU-02 (ver Flujo). Recibe `RepositorioPracticas`, `Bitacora` y un `reloj` inyectable, como `PostularsePlaza` |

Se reutilizan sin cambios: `Bitacora`, `ProveedorIdentidad`, `UsuarioAutenticado`, `ErrorAplicacion`, `NoAutenticado` y `AccesoDenegado`.

### infraestructura (`src/infraestructura/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `src/infraestructura/repositorio_practicas_memoria.py` **(cambia)** | `RepositorioPracticasMemoria` | Agrega un diccionario de empresas, `agregar_empresa(empresa)` para precargar, `obtener_empresa`, `guardar_plaza` y `listar_plazas()` para la evidencia. `agregar_plaza` y lo de CU-01 no cambian |
| `src/infraestructura/controlador_rest.py` **(cambia)** | `ControladorRest` | Recibe también `PublicarPlaza`. Agrega `publicar_plaza(token, cuerpo)`, que representa "POST /plazas": valida el token, arma `SolicitudPublicacionPlaza` con `id_empresa`, `cargo`, `cupos` y `periodo` del cuerpo, llama al caso de uso y responde 201 con el DTO y el mensaje "plaza publicada". Amplía la tabla de errores: 400 `PlazaNoValida` y 404 `EmpresaNoEncontrada`; incluye el `motivo` en la respuesta también para `PlazaNoValida`. `postular` no cambia |
| `src/main.py` **(cambia)** | (composición) | Crea `PublicarPlaza` y lo pasa al controlador. Precarga la Empresa "EMP-ACME" "Acme S.A.S." y el token del Coordinador "C-01" con el rol `CoordinadorPracticas`, según los Antecedentes de la spec. Lo de CU-01 se conserva |

Vista de usos: Módulo Postulaciones → dominio. No usa otros módulos, así que no hay ciclos.

## Flujo

CU-02 no es caso de uso primario, así que no tiene diagrama en [docs/diagramas/secuencias/](../../docs/diagramas/secuencias/) (drivers.md, sección 6). Sigue la misma forma de [cu01-postularse.puml](../../docs/diagramas/secuencias/cu01-postularse.puml): Controlador REST → Validador de token → caso de uso → RepositorioPracticas y Bitacora.

1. `ControladorRest.publicar_plaza` recibe "POST /plazas" con el token y el cuerpo (`id_empresa`, `cargo`, `cupos`, `periodo`).
2. `ValidadorToken` valida el token con `ProveedorIdentidad`. Si es inválido o venció, responde 401 y no llama al caso de uso.
3. `PublicarPlaza.ejecutar(SolicitudPublicacionPlaza)`:
   1. Si el rol no es `CoordinadorPracticas`, registra en la `Bitacora` el acceso rechazado (usuario, rol, recurso `empresa:<id>`, acción "publicar plaza", hora) y lanza `AccesoDenegado`.
   2. Obtiene la `Empresa`. Si no existe, lanza `EmpresaNoEncontrada`.
   3. Si `Plaza.motivo_invalidez(cargo, cupos, periodo)` devuelve un motivo, lanza `PlazaNoValida(motivo)`.
   4. Crea la `Plaza` con el id `PL-<8 hex>` (misma forma que `PO-<8 hex>` de CU-01) y la guarda con `guardar_plaza`. No escribe en la bitácora.
   5. Devuelve `PlazaPublicada`.
4. `ControladorRest` responde 201 con el DTO, o traduce el error de aplicación (ADR-007).

Una Plaza publicada queda disponible para `PostularsePlaza` de CU-01 porque ambos usan el mismo repositorio (escenario del flujo alterno con CU-01). Como no hay control de duplicados, dos plazas iguales reciben ids distintos.

## Fuera de alcance

- Editar, cerrar o eliminar plazas (decisión de la spec).
- CU-14 (gestionar empresas y representantes): la Empresa se precarga en `main.py`; el NIT se agrega con ese caso de uso.
- Servidor HTTP real y framework web: ningún ADR aprueba una librería. El controlador recibe y devuelve estructuras de Python, como en CU-01.
- PostgreSQL, transacciones reales e integración real con el SSO: adaptadores en memoria o simulados en esta etapa.
- Aplicación web (ADR-010) y notificaciones por correo: CU-02 no envía correos.
- Pruebas automatizadas: la validación se hace escenario por escenario, con evidencia (`validacion.md`).
