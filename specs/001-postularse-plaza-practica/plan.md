# Plan: 001 Postularse a una plaza de práctica

Aterriza [spec.md](spec.md) (CU-01) en la arquitectura de [docs/arquitectura.md](../../docs/arquitectura.md). No agrega componentes fuera de [vistas/03-desarrollo.md](../../docs/vistas/03-desarrollo.md).

## Decisiones que aplican

| ID | Qué aplica a CU-01 |
|----|--------------------|
| ADR-002 | El caso de uso vive en el Módulo Postulaciones. Capas `dominio/`, `aplicacion/` e `infraestructura/` bajo `src/`. `dominio/` no importa nada de las otras capas. Los puertos son `Protocol` en `aplicacion/puertos/`. |
| ADR-003 | El Adaptador PostgreSQL implementa RepositorioPracticas. En esta etapa se usa un adaptador en memoria con el mismo puerto (`AGENTS.md`). |
| ADR-004 | El Validador de token valida el token de corta vida (15 minutos) con el puerto ProveedorIdentidad y entrega la identidad y el rol. La autorización por rol (solo Estudiante se postula) se hace **en el caso de uso**, no en el controlador. El Adaptador SSO se simula (R-03). |
| ADR-006 | El caso de uso escribe en la bitácora por el puerto `Bitacora`: la creación de la Postulacion "enviada" y cada acceso rechazado, con usuario, rol, recurso, acción y hora, en la misma unidad de trabajo que el cambio. Los rechazos por regla de negocio no se auditan (decisión de la spec). |
| ADR-007 | El caso de uso lanza errores de aplicación propios. El Controlador REST los convierte en la respuesta unificada (código, mensaje e identificador de correlación). |
| ADR-008 | No aplica: CU-01 no usa ReglaPractica. |
| Vista lógica (01-logica.md) | Plaza (cargo, cupos, periodo), Postulacion (fecha, estado: enviada, aceptada, rechazada), Estudiante. Reglas: a lo sumo una Postulacion aceptada por Estudiante y periodo; no más aceptadas que cupos. |
| Vista de desarrollo (03-desarrollo.md) | Controlador REST, Validador de token, Módulo Postulaciones, puertos RepositorioPracticas, Bitacora y ProveedorIdentidad, sus adaptadores y `main.py` como composición. |

## Componentes

Python 3.12, una clase por archivo, sin `__init__.py`, nombres del glosario.

### dominio (`src/dominio/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `src/dominio/estado_postulacion.py` | `EstadoPostulacion` (Enum) | Valores `ENVIADA`, `ACEPTADA` y `RECHAZADA` |
| `src/dominio/plaza.py` | `Plaza` | id, id de la empresa, cargo, cupos y periodo. `tiene_cupo(aceptadas: int) -> bool` aplica "no más aceptadas que cupos" |
| `src/dominio/postulacion.py` | `Postulacion` | id, id del estudiante, id de la plaza, periodo, fecha y estado. `Postulacion.enviar(...)` crea una postulación en estado `ENVIADA` |

### aplicacion (`src/aplicacion/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `src/aplicacion/puertos/repositorio_practicas.py` | `RepositorioPracticas` (Protocol) | `obtener_plaza(id_plaza) -> Plaza \| None`; `contar_postulaciones_aceptadas(id_plaza) -> int`; `tiene_postulacion_aceptada_en_periodo(id_estudiante, periodo) -> bool`; `existe_postulacion(id_estudiante, id_plaza) -> bool`; `guardar_postulacion(postulacion) -> None` |
| `src/aplicacion/puertos/bitacora.py` | `Bitacora` (Protocol) | `registrar(usuario, rol, recurso, accion, hora) -> None` |
| `src/aplicacion/puertos/proveedor_identidad.py` | `ProveedorIdentidad` (Protocol) | `validar(token) -> UsuarioAutenticado`; lanza `NoAutenticado` si el token es inválido o venció |
| `src/aplicacion/usuario_autenticado.py` | `UsuarioAutenticado` (DTO) | id del usuario y rol, tal como los entrega el Validador de token |
| `src/aplicacion/postulaciones/solicitud_postulacion.py` | `SolicitudPostulacion` (DTO de entrada) | usuario autenticado e id de la plaza |
| `src/aplicacion/postulaciones/postulacion_enviada.py` | `PostulacionEnviada` (DTO de salida) | id de la postulación, id de la plaza, estado y fecha |
| `src/aplicacion/postulaciones/postularse_plaza.py` | `PostularsePlaza` | Caso de uso de CU-01 (ver Flujo) |
| `src/aplicacion/errores/error_aplicacion.py` | `ErrorAplicacion` | Base del catálogo de errores (ADR-007): código y mensaje |
| `src/aplicacion/errores/no_autenticado.py` | `NoAutenticado` | Token ausente, inválido o vencido |
| `src/aplicacion/errores/acceso_denegado.py` | `AccesoDenegado` | El usuario no tiene el rol requerido |
| `src/aplicacion/errores/plaza_no_encontrada.py` | `PlazaNoEncontrada` | La plaza no existe |
| `src/aplicacion/errores/postulacion_no_permitida.py` | `PostulacionNoPermitida` | Sin cupos, con una aceptada en el periodo o ya postulado a la plaza; lleva el motivo |

### infraestructura (`src/infraestructura/`)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `src/infraestructura/controlador_rest.py` | `ControladorRest` | Recibe la petición "POST /postulaciones" (token y cuerpo como datos de Python), pide la identidad al `ValidadorToken`, arma el DTO, llama a `PostularsePlaza` y traduce el resultado o el error a la respuesta unificada: 201, 401 `NoAutenticado`, 403 `AccesoDenegado`, 404 `PlazaNoEncontrada` y 409 `PostulacionNoPermitida`, con código, mensaje e identificador de correlación |
| `src/infraestructura/validador_token.py` | `ValidadorToken` | Usa `ProveedorIdentidad` y entrega un `UsuarioAutenticado` |
| `src/infraestructura/proveedor_identidad_simulado.py` | `ProveedorIdentidadSimulado` | Adaptador SSO simulado: tokens precargados con usuario, rol y hora de emisión. Rechaza los que tienen más de 15 minutos |
| `src/infraestructura/repositorio_practicas_memoria.py` | `RepositorioPracticasMemoria` | Implementa `RepositorioPracticas` con diccionarios, con plazas y postulaciones precargables |
| `src/infraestructura/bitacora_memoria.py` | `BitacoraMemoria` | Implementa `Bitacora` con una lista consultable para la evidencia |
| `src/main.py` | (composición) | Crea los adaptadores en memoria, el caso de uso, el validador y el controlador, y carga los datos de los Antecedentes de la spec |

Vista de usos: Módulo Postulaciones → dominio. No usa otros módulos, así que no hay ciclos.

## Flujo

Diagrama: [docs/diagramas/secuencias/cu01-postularse.puml](../../docs/diagramas/secuencias/cu01-postularse.puml) (ESC-01).

1. `ControladorRest` recibe "POST /postulaciones" con el token y el id de la plaza.
2. `ValidadorToken` valida el token con `ProveedorIdentidad`. Si es inválido o vencido, responde 401 y no llama al caso de uso.
3. `PostularsePlaza.ejecutar(SolicitudPostulacion)`:
   1. Si el rol no es `Estudiante`, registra en la `Bitacora` el acceso rechazado (usuario, rol, recurso plaza, acción "postularse", hora) y lanza `AccesoDenegado`.
   2. Obtiene la `Plaza`. Si no existe, lanza `PlazaNoEncontrada`.
   3. Si `existe_postulacion(estudiante, plaza)`, lanza `PostulacionNoPermitida("ya te postulaste a esta plaza")`.
   4. Si `tiene_postulacion_aceptada_en_periodo(estudiante, plaza.periodo)`, lanza `PostulacionNoPermitida("ya tienes una postulación aceptada en el periodo")`.
   5. Si `not plaza.tiene_cupo(contar_postulaciones_aceptadas(plaza))`, lanza `PostulacionNoPermitida("la plaza no tiene cupos disponibles")`.
   6. Crea `Postulacion.enviar(...)`, la guarda y registra en la `Bitacora` la acción "crear con estado enviada", en la misma unidad de trabajo (ADR-006). Con los adaptadores en memoria, la bitácora se escribe justo después de guardar, en la misma llamada.
   7. Devuelve `PostulacionEnviada`.
4. `ControladorRest` responde 201 con el DTO, o traduce el error de aplicación (ADR-007).

Como el cupo se consume al aceptar, dos postulaciones simultáneas al último cupo quedan ambas "enviadas" (escenario de concurrencia). No hace falta un bloqueo.

## Fuera de alcance

- Aceptar o rechazar una Postulacion y crear la Practica: no hay un caso de uso que lo cubra en el catálogo.
- CU-02 (publicar plazas) y CU-14 (gestionar empresas): las plazas y la empresa se precargan en `main.py`.
- Servidor HTTP real y framework web: ningún ADR aprueba una librería. El controlador recibe y devuelve estructuras de Python. Exponerlo por HTTP requiere un ADR nuevo.
- PostgreSQL, transacciones reales e integración real con el SSO: adaptadores en memoria o simulados en esta etapa.
- Aplicación web (ADR-010) y notificaciones por correo: CU-01 no envía correos.
- Pruebas automatizadas: la validación se hace escenario por escenario, con evidencia (`validacion.md`).
