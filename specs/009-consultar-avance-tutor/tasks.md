# Tareas: 009 Consultar el avance de los estudiantes asignados

Derivadas de [plan.md](plan.md). Una tarea por clase o archivo, de adentro hacia afuera. En los commits se escribe "009 T-NN". Nombres de escenario según [spec.md](spec.md):

| Clave | Escenario |
|-------|-----------|
| ESC-B | Flujo básico - el Tutor consulta el avance de sus prácticas |
| ESC-UNA | Flujo alterno - el Tutor consulta una sola práctica suya |
| ESC-VAC | Flujo alterno - un tutor sin prácticas asignadas |
| ESC-VR | Flujo alterno - cuentan las horas requeridas de la versión de la práctica |
| ESC-AJ | EAC-04 - un tutor consulta una práctica que no tiene asignada |
| ESC-SR | Excepción - un usuario sin el rol Tutor consulta el avance |
| ESC-PN | Excepción - la práctica no existe |
| ESC-TV | Excepción - petición con token vencido |

## Aplicación

- [x] T-01 Puerto RepositorioPracticas: prácticas de un tutor y registros de una práctica
      Archivos: src/aplicacion/puertos/repositorio_practicas.py
      Escenarios: ESC-B, ESC-UNA, ESC-VAC, ESC-VR
      Depende de: ninguna

- [x] T-02 DTO ResumenHoras
      Archivos: src/aplicacion/horas/resumen_horas.py
      Escenarios: ESC-B, ESC-UNA, ESC-VR
      Depende de: ninguna

- [x] T-03 Caso de uso ResumirHorasPractica (Módulo Horas, solo lectura)
      Archivos: src/aplicacion/horas/resumir_horas_practica.py
      Escenarios: ESC-B, ESC-UNA, ESC-VR
      Depende de: T-01, T-02

- [ ] T-04 DTO SolicitudAvanceTutor
      Archivos: src/aplicacion/seguimiento/solicitud_avance_tutor.py
      Escenarios: ESC-B, ESC-UNA, ESC-AJ, ESC-SR
      Depende de: ninguna

- [ ] T-05 DTO AvancePractica
      Archivos: src/aplicacion/seguimiento/avance_practica.py
      Escenarios: ESC-B, ESC-UNA, ESC-VR
      Depende de: ninguna

- [ ] T-06 DTO AvanceTutor
      Archivos: src/aplicacion/seguimiento/avance_tutor.py
      Escenarios: ESC-B, ESC-VAC
      Depende de: T-05

- [ ] T-07 Caso de uso ConsultarAvanceTutor
      Archivos: src/aplicacion/seguimiento/consultar_avance_tutor.py
      Escenarios: todos menos ESC-TV
      Depende de: T-01, T-03, T-04, T-06

## Infraestructura

- [ ] T-08 RepositorioPracticasMemoria: prácticas de un tutor y registros de una práctica
      Archivos: src/infraestructura/repositorio_practicas_memoria.py
      Escenarios: ESC-B, ESC-UNA, ESC-VAC, ESC-VR
      Depende de: T-01

- [ ] T-09 ControladorRest: consultar_avance (GET /tutores/yo/avance y GET /practicas/{id}/avance)
      Archivos: src/infraestructura/controlador_rest.py
      Escenarios: todos
      Depende de: T-07

## Composición

- [ ] T-10 Composición en main.py con ConsultarAvanceTutor y los datos de los Antecedentes
      Archivos: src/main.py
      Escenarios: todos
      Depende de: T-08, T-09

## Validación

- [ ] T-11 Validar escenario por escenario y registrar la evidencia
      Archivos: specs/009-consultar-avance-tutor/validacion.md
      Escenarios: todos
      Depende de: T-10
