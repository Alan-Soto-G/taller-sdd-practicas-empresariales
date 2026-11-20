C# Tareas: 001 Postularse a una plaza de práctica

Derivadas de [plan.md](plan.md). Una tarea por clase o archivo, de adentro hacia afuera. Nombres de escenario según [spec.md](spec.md):

| Clave | Escenario |
|-------|-----------|
| ESC-B | Flujo básico - el Estudiante se postula a una plaza con cupos |
| ESC-SC | Excepción - la plaza no tiene cupos disponibles |
| ESC-AP | Excepción - el Estudiante ya tiene una postulación aceptada en el periodo |
| ESC-OP | Flujo alterno - una postulación aceptada en otro periodo no impide postularse |
| ESC-MP | Excepción - el Estudiante ya se postuló a la misma plaza (esquema: enviada, rechazada) |
| ESC-VP | Flujo alterno - el Estudiante tiene postulaciones enviadas a otras plazas |
| ESC-NE | Excepción - la plaza no existe |
| ESC-SR | Excepción - un usuario sin el rol Estudiante intenta postularse |
| ESC-TV | Excepción - petición con token vencido |
| ESC-CC | Concurrencia - dos estudiantes se postulan cuando queda un solo cupo |

## Dominio

- [x] T-01 Enum EstadoPostulacion
      Archivos: src/dominio/estado_postulacion.py
      Escenarios: ESC-B, ESC-AP, ESC-OP, ESC-MP, ESC-VP
      Depende de: ninguna

- [x] T-02 Entidad Plaza con la regla de cupos
      Archivos: src/dominio/plaza.py
      Escenarios: ESC-B, ESC-SC, ESC-CC
      Depende de: ninguna

- [x] T-03 Entidad Postulacion con la creación en estado enviada
      Archivos: src/dominio/postulacion.py
      Escenarios: ESC-B, ESC-OP, ESC-VP, ESC-CC
      Depende de: T-01

## Aplicación: errores (ADR-007)

- [x] T-04 Error base ErrorAplicacion
      Archivos: src/aplicacion/errores/error_aplicacion.py
      Escenarios: ESC-SC, ESC-AP, ESC-MP, ESC-NE, ESC-SR, ESC-TV
      Depende de: ninguna

- [x] T-05 Error NoAutenticado
      Archivos: src/aplicacion/errores/no_autenticado.py
      Escenarios: ESC-TV
      Depende de: T-04

- [x] T-06 Error AccesoDenegado
      Archivos: src/aplicacion/errores/acceso_denegado.py
      Escenarios: ESC-SR
      Depende de: T-04

- [ ] T-07 Error PlazaNoEncontrada
      Archivos: src/aplicacion/errores/plaza_no_encontrada.py
      Escenarios: ESC-NE
      Depende de: T-04

- [ ] T-08 Error PostulacionNoPermitida con su motivo
      Archivos: src/aplicacion/errores/postulacion_no_permitida.py
      Escenarios: ESC-SC, ESC-AP, ESC-MP
      Depende de: T-04

## Aplicación: DTO y puertos

- [ ] T-09 DTO UsuarioAutenticado
      Archivos: src/aplicacion/usuario_autenticado.py
      Escenarios: ESC-B, ESC-SR, ESC-TV
      Depende de: ninguna

- [ ] T-10 Puerto RepositorioPracticas
      Archivos: src/aplicacion/puertos/repositorio_practicas.py
      Escenarios: ESC-B, ESC-SC, ESC-AP, ESC-OP, ESC-MP, ESC-VP, ESC-NE, ESC-CC
      Depende de: T-02, T-03

- [ ] T-11 Puerto Bitacora
      Archivos: src/aplicacion/puertos/bitacora.py
      Escenarios: ESC-B, ESC-SC, ESC-SR
      Depende de: ninguna

- [ ] T-12 Puerto ProveedorIdentidad
      Archivos: src/aplicacion/puertos/proveedor_identidad.py
      Escenarios: ESC-TV
      Depende de: T-05, T-09

- [ ] T-13 DTO de entrada SolicitudPostulacion
      Archivos: src/aplicacion/postulaciones/solicitud_postulacion.py
      Escenarios: ESC-B
      Depende de: T-09

- [ ] T-14 DTO de salida PostulacionEnviada
      Archivos: src/aplicacion/postulaciones/postulacion_enviada.py
      Escenarios: ESC-B
      Depende de: T-01

## Aplicación: caso de uso

- [ ] T-15 Caso de uso PostularsePlaza
      Archivos: src/aplicacion/postulaciones/postularse_plaza.py
      Escenarios: ESC-B, ESC-SC, ESC-AP, ESC-OP, ESC-MP, ESC-VP, ESC-NE, ESC-SR, ESC-CC
      Depende de: T-02, T-03, T-06, T-07, T-08, T-10, T-11, T-13, T-14

## Infraestructura: adaptadores

- [ ] T-16 Adaptador RepositorioPracticasMemoria
      Archivos: src/infraestructura/repositorio_practicas_memoria.py
      Escenarios: ESC-B, ESC-SC, ESC-AP, ESC-OP, ESC-MP, ESC-VP, ESC-NE, ESC-CC
      Depende de: T-10

- [ ] T-17 Adaptador BitacoraMemoria
      Archivos: src/infraestructura/bitacora_memoria.py
      Escenarios: ESC-B, ESC-SC, ESC-SR
      Depende de: T-11

- [ ] T-18 Adaptador ProveedorIdentidadSimulado (tokens de 15 minutos)
      Archivos: src/infraestructura/proveedor_identidad_simulado.py
      Escenarios: ESC-TV, ESC-SR
      Depende de: T-12

- [ ] T-19 Adaptador de entrada ValidadorToken
      Archivos: src/infraestructura/validador_token.py
      Escenarios: ESC-TV
      Depende de: T-12

- [ ] T-20 ControladorRest con la respuesta unificada (201, 401, 403, 404, 409)
      Archivos: src/infraestructura/controlador_rest.py
      Escenarios: ESC-B, ESC-SC, ESC-AP, ESC-MP, ESC-NE, ESC-SR, ESC-TV
      Depende de: T-15, T-19

## Composición

- [ ] T-21 Composición en main.py con los datos de los Antecedentes
      Archivos: src/main.py
      Escenarios: todos
      Depende de: T-16, T-17, T-18, T-20

## Validación

- [ ] T-22 Validar escenario por escenario y registrar la evidencia
      Archivos: specs/001-postularse-plaza-practica/validacion.md
      Escenarios: todos (ESC-B, ESC-SC, ESC-AP, ESC-OP, ESC-MP, ESC-VP, ESC-NE, ESC-SR, ESC-TV, ESC-CC)
      Depende de: T-21
