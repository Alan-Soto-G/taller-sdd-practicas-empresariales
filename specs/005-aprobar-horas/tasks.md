# Tareas: 005 Aprobar horas reportadas

Derivadas de [plan.md](plan.md). Una tarea por clase o archivo, de adentro hacia afuera. En los commits se escribe "005 T-NN". Nombres de escenario según [spec.md](spec.md):

| Clave | Escenario |
|-------|-----------|
| ESC-B | Flujo básico - el Tutor aprueba las horas reportadas |
| ESC-RE | Flujo alterno - el Tutor rechaza las horas reportadas |
| ESC-HC | Flujo alterno - la aprobación completa las horas requeridas |
| ESC-VR | Flujo alterno - cuentan las horas requeridas de la versión de la práctica, no las de la vigente |
| ESC-YR | Excepción - el registro ya fue revisado (esquema: aprobado, rechazado) |
| ESC-DI | Excepción - la decisión no es aprobar ni rechazar |
| ESC-RN | Excepción - el registro no existe |
| ESC-AJ | EAC-04 - un tutor que no está asignado intenta aprobar las horas |
| ESC-ET | Excepción - el Estudiante titular intenta aprobar sus propias horas |
| ESC-TV | Excepción - petición con token vencido |

## Dominio

- [x] T-01 RegistroHoras: aprobar y rechazar
      Archivos: src/dominio/registro_horas.py
      Escenarios: ESC-B, ESC-RE, ESC-YR
      Depende de: ninguna

- [x] T-02 Practica: completar_horas
      Archivos: src/dominio/practica.py
      Escenarios: ESC-HC, ESC-VR
      Depende de: ninguna

## Aplicación: errores, puertos, configuración y DTO

- [x] T-03 Error RegistroNoEncontrado
      Archivos: src/aplicacion/errores/registro_no_encontrado.py
      Escenarios: ESC-RN
      Depende de: ninguna

- [x] T-04 Puerto RepositorioPracticas: obtener_regla, obtener_registro_horas, actualizar_registro_horas y sumar_horas_aprobadas
      Archivos: src/aplicacion/puertos/repositorio_practicas.py
      Escenarios: todos menos ESC-TV
      Depende de: T-01

- [x] T-05 Caso de uso ConsultarHorasRequeridas (Módulo Configuración)
      Archivos: src/aplicacion/configuracion/consultar_horas_requeridas.py
      Escenarios: ESC-HC, ESC-VR
      Depende de: T-04

- [x] T-06 DTO de entrada SolicitudRevisionHoras
      Archivos: src/aplicacion/horas/solicitud_revision_horas.py
      Escenarios: ESC-B, ESC-RE, ESC-DI, ESC-AJ, ESC-ET
      Depende de: ninguna

- [x] T-07 DTO de salida HorasRevisadas
      Archivos: src/aplicacion/horas/horas_revisadas.py
      Escenarios: ESC-B, ESC-RE, ESC-HC, ESC-VR
      Depende de: ninguna

## Aplicación: caso de uso

- [x] T-08 Caso de uso AprobarHoras
      Archivos: src/aplicacion/horas/aprobar_horas.py
      Escenarios: todos menos ESC-TV
      Depende de: T-01, T-02, T-03, T-04, T-05, T-06, T-07

## Infraestructura: adaptadores

- [x] T-09 RepositorioPracticasMemoria: reglas por versión, registros por id, actualización y suma de horas aprobadas
      Archivos: src/infraestructura/repositorio_practicas_memoria.py
      Escenarios: todos menos ESC-TV
      Depende de: T-04

- [x] T-10 ControladorRest: revisar_horas (POST /registros-horas/{id}/revision) con 200 y 404
      Archivos: src/infraestructura/controlador_rest.py
      Escenarios: ESC-B, ESC-RE, ESC-YR, ESC-DI, ESC-RN, ESC-AJ, ESC-ET, ESC-TV
      Depende de: T-08

## Composición

- [ ] T-11 Composición en main.py con AprobarHoras y los datos de los Antecedentes
      Archivos: src/main.py
      Escenarios: todos
      Depende de: T-05, T-09, T-10

## Validación

- [ ] T-12 Validar escenario por escenario y registrar la evidencia
      Archivos: specs/005-aprobar-horas/validacion.md
      Escenarios: todos
      Depende de: T-11
