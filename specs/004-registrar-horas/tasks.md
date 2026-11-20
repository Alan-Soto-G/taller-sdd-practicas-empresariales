# Tareas: 004 Registrar horas de práctica

Derivadas de [plan.md](plan.md). Una tarea por clase o archivo, de adentro hacia afuera. En los commits se escribe "004 T-NN". Nombres de escenario según [spec.md](spec.md):

| Clave | Escenario |
|-------|-----------|
| ESC-B | Flujo básico - el Estudiante registra las horas de una semana |
| ESC-OS | Flujo alterno - el Estudiante registra otra semana |
| ESC-SR2 | Excepción - la semana ya tiene un registro |
| ESC-DI | Excepción - las horas o los datos están fuera del rango permitido (esquema: 0, -5, 169, sin actividades, semana 2026-47 y 2026-W54) |
| ESC-NC | Excepción - la práctica no está en curso |
| ESC-PN | Excepción - la práctica no existe |
| ESC-AJ | EAC-04 - un estudiante intenta registrar horas en una práctica ajena |
| ESC-SR | Excepción - un usuario sin el rol Estudiante intenta registrar horas |
| ESC-TV | Excepción - petición con token vencido |
| ESC-CA | EAC-01 - 300 estudiantes registran sus horas al mismo tiempo en el cierre |
| ESC-DU | EAC-01 - el mismo registro llega dos veces al mismo tiempo |

## Dominio

- [x] T-01 Enum EstadoRegistroHoras
      Archivos: src/dominio/estado_registro_horas.py
      Escenarios: ESC-B, ESC-OS
      Depende de: ninguna

- [x] T-02 Entidad RegistroHoras con reportar y motivo_invalidez
      Archivos: src/dominio/registro_horas.py
      Escenarios: ESC-B, ESC-OS, ESC-DI
      Depende de: T-01

## Aplicación: errores (ADR-007)

- [x] T-03 Error PracticaNoEncontrada
      Archivos: src/aplicacion/errores/practica_no_encontrada.py
      Escenarios: ESC-PN
      Depende de: ninguna

- [x] T-04 Error RegistroNoValido con su motivo
      Archivos: src/aplicacion/errores/registro_no_valido.py
      Escenarios: ESC-SR2, ESC-DI, ESC-NC, ESC-DU
      Depende de: ninguna

## Aplicación: puertos y DTO

- [x] T-05 Puerto RepositorioPracticas: existe_registro_horas y guardar_registro_horas
      Archivos: src/aplicacion/puertos/repositorio_practicas.py
      Escenarios: ESC-B, ESC-OS, ESC-SR2, ESC-CA, ESC-DU
      Depende de: T-02

- [x] T-06 DTO de entrada SolicitudRegistroHoras
      Archivos: src/aplicacion/horas/solicitud_registro_horas.py
      Escenarios: ESC-B, ESC-AJ, ESC-SR
      Depende de: ninguna

- [x] T-07 DTO de salida HorasReportadas
      Archivos: src/aplicacion/horas/horas_reportadas.py
      Escenarios: ESC-B, ESC-OS
      Depende de: ninguna

## Aplicación: caso de uso

- [x] T-08 Caso de uso RegistrarHoras
      Archivos: src/aplicacion/horas/registrar_horas.py
      Escenarios: todos menos ESC-TV
      Depende de: T-02, T-03, T-04, T-05, T-06, T-07

## Infraestructura: adaptadores

- [x] T-09 RepositorioPracticasMemoria: registros de horas con guardado atómico
      Archivos: src/infraestructura/repositorio_practicas_memoria.py
      Escenarios: ESC-B, ESC-OS, ESC-SR2, ESC-CA, ESC-DU
      Depende de: T-05

- [x] T-10 ControladorRest: registrar_horas (POST /practicas/{id}/horas) con 201, 404 y 422
      Archivos: src/infraestructura/controlador_rest.py
      Escenarios: ESC-B, ESC-SR2, ESC-DI, ESC-NC, ESC-PN, ESC-AJ, ESC-SR, ESC-TV, ESC-DU
      Depende de: T-08

## Composición

- [ ] T-11 Composición en main.py con RegistrarHoras y los datos de los Antecedentes
      Archivos: src/main.py
      Escenarios: todos
      Depende de: T-09, T-10

## Validación

- [ ] T-12 Validar escenario por escenario y registrar la evidencia
      Archivos: specs/004-registrar-horas/validacion.md
      Escenarios: todos
      Depende de: T-11
