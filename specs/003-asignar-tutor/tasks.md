# Tareas: 003 Asignar tutor a un estudiante

Derivadas de [plan.md](plan.md). Una tarea por clase o archivo, de adentro hacia afuera. En los commits se escribe "003 T-NN". Nombres de escenario según [spec.md](spec.md):

| Clave | Escenario |
|-------|-----------|
| ESC-B | Flujo básico - el Coordinador asigna un tutor con cupo a una práctica sin tutor |
| ESC-VA | Flujo alterno - el Coordinador asigna el mismo tutor a varias prácticas a la vez |
| ESC-SC | Excepción - el tutor ya alcanzó su carga máxima |
| ESC-CE | Flujo alterno - una práctica cerrada no cuenta en la carga del tutor |
| ESC-CP | Flujo alterno - el tutor tiene cupo solo para una parte de las prácticas seleccionadas |
| ESC-CO | Flujo alterno - el correo de notificación falla |
| ESC-RV | Flujo alterno - un cambio de la carga máxima aplica a las asignaciones siguientes |
| ESC-YT | Excepción - la práctica ya tiene tutor |
| ESC-PN | Excepción - la práctica no existe |
| ESC-TN | Excepción - el tutor no existe |
| ESC-SR | Excepción - un usuario sin el rol CoordinadorPracticas intenta asignar un tutor |
| ESC-TV | Excepción - petición con token vencido |

## Dominio

- [x] T-01 Enum EstadoPractica
      Archivos: src/dominio/estado_practica.py
      Escenarios: ESC-B, ESC-SC, ESC-CE, ESC-YT
      Depende de: ninguna

- [x] T-02 Entidad Practica con asignar_tutor y esta_activa
      Archivos: src/dominio/practica.py
      Escenarios: ESC-B, ESC-VA, ESC-CE, ESC-YT
      Depende de: T-01

- [x] T-03 Entidad Tutor con la regla tiene_cupo
      Archivos: src/dominio/tutor.py
      Escenarios: ESC-B, ESC-SC, ESC-CP, ESC-RV
      Depende de: ninguna

- [x] T-04 Entidad Estudiante
      Archivos: src/dominio/estudiante.py
      Escenarios: ESC-B
      Depende de: ninguna

- [x] T-05 Entidad ReglaPractica
      Archivos: src/dominio/regla_practica.py
      Escenarios: ESC-SC, ESC-RV
      Depende de: ninguna

## Aplicación: errores (ADR-007)

- [x] T-06 Error TutorNoEncontrado
      Archivos: src/aplicacion/errores/tutor_no_encontrado.py
      Escenarios: ESC-TN
      Depende de: ninguna

- [x] T-07 Error CorreoNoEnviado
      Archivos: src/aplicacion/errores/correo_no_enviado.py
      Escenarios: ESC-CO
      Depende de: ninguna

## Aplicación: puertos y DTO

- [x] T-08 Puerto Notificador
      Archivos: src/aplicacion/puertos/notificador.py
      Escenarios: ESC-B, ESC-CO
      Depende de: T-07

- [x] T-09 Puerto RepositorioPracticas: reglas, tutores, estudiantes y prácticas
      Archivos: src/aplicacion/puertos/repositorio_practicas.py
      Escenarios: todos menos ESC-TV
      Depende de: T-02, T-03, T-04, T-05

- [x] T-10 DTO ReglaVigente
      Archivos: src/aplicacion/configuracion/regla_vigente.py
      Escenarios: ESC-SC, ESC-RV
      Depende de: ninguna

- [ ] T-11 Caso de uso ConsultarReglaVigente (Módulo Configuración)
      Archivos: src/aplicacion/configuracion/consultar_regla_vigente.py
      Escenarios: ESC-SC, ESC-RV
      Depende de: T-09, T-10

- [ ] T-12 DTO de entrada SolicitudAsignacionTutor
      Archivos: src/aplicacion/asignacion/solicitud_asignacion_tutor.py
      Escenarios: ESC-B, ESC-VA, ESC-SR
      Depende de: ninguna

- [ ] T-13 DTO ResultadoPractica
      Archivos: src/aplicacion/asignacion/resultado_practica.py
      Escenarios: ESC-B, ESC-SC, ESC-CP, ESC-YT, ESC-PN
      Depende de: ninguna

- [ ] T-14 DTO de salida AsignacionRealizada
      Archivos: src/aplicacion/asignacion/asignacion_realizada.py
      Escenarios: ESC-B, ESC-VA, ESC-CP
      Depende de: T-13

## Aplicación: caso de uso

- [ ] T-15 Caso de uso AsignarTutor
      Archivos: src/aplicacion/asignacion/asignar_tutor.py
      Escenarios: todos menos ESC-TV
      Depende de: T-02, T-03, T-06, T-07, T-08, T-09, T-11, T-12, T-14

## Infraestructura: adaptadores

- [ ] T-16 Adaptador NotificadorSimulado (enviados y pendientes de reenvío)
      Archivos: src/infraestructura/notificador_simulado.py
      Escenarios: ESC-B, ESC-CO, ESC-SC, ESC-TN
      Depende de: T-07

- [ ] T-17 RepositorioPracticasMemoria: reglas, tutores, estudiantes y prácticas
      Archivos: src/infraestructura/repositorio_practicas_memoria.py
      Escenarios: todos menos ESC-TV
      Depende de: T-09

- [ ] T-18 ControladorRest: asignar_tutor (POST /asignaciones) con 200 y 404
      Archivos: src/infraestructura/controlador_rest.py
      Escenarios: ESC-B, ESC-TN, ESC-SR, ESC-TV
      Depende de: T-15

## Composición

- [ ] T-19 Composición en main.py con AsignarTutor y los datos de los Antecedentes
      Archivos: src/main.py
      Escenarios: todos
      Depende de: T-11, T-15, T-16, T-17, T-18

## Validación

- [ ] T-20 Validar escenario por escenario y registrar la evidencia
      Archivos: specs/003-asignar-tutor/validacion.md
      Escenarios: todos
      Depende de: T-19
