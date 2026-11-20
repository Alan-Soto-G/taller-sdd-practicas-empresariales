# Tareas: 010 Consultar el estado de la práctica y del acta

Derivadas de [plan.md](plan.md). Una tarea por clase o archivo, de adentro hacia afuera. En los commits se escribe "010 T-NN". Desde CU-10 las tareas las implementa Claude directamente, sin obreros, a pedido del usuario. Nombres de escenario según [spec.md](spec.md):

| Clave | Escenario |
|-------|-----------|
| ESC-B | Flujo básico - el Estudiante consulta su práctica evaluada |
| ESC-EC | Flujo alterno - práctica en curso, sin evaluación ni acta |
| ESC-AC | Flujo alterno - práctica con el acta esperando aprobaciones |
| ESC-TO | Flujo alterno - el Estudiante consulta todas sus prácticas |
| ESC-AJ | EAC-04 - un estudiante intenta consultar la práctica de otro |
| ESC-SR | Excepción - un usuario sin el rol Estudiante usa CU-10 |
| ESC-PN | Excepción - la práctica no existe |
| ESC-TV | Excepción - petición con token vencido |

## Aplicación

- [x] T-01 Puerto RepositorioPracticas: prácticas de un estudiante
      Archivos: src/aplicacion/puertos/repositorio_practicas.py
      Escenarios: ESC-TO
      Depende de: ninguna

- [ ] T-02 DTO ResumenActa
      Archivos: src/aplicacion/actas/resumen_acta.py
      Escenarios: ESC-AC
      Depende de: ninguna

- [ ] T-03 Caso de uso ConsultarActaPractica (Módulo Actas, solo lectura)
      Archivos: src/aplicacion/actas/consultar_acta_practica.py
      Escenarios: ESC-B, ESC-EC, ESC-AC
      Depende de: T-02

- [ ] T-04 DTO SolicitudEstadoPractica
      Archivos: src/aplicacion/seguimiento/solicitud_estado_practica.py
      Escenarios: todos menos ESC-TV
      Depende de: ninguna

- [ ] T-05 DTO EstadoPracticaConsultado
      Archivos: src/aplicacion/seguimiento/estado_practica_consultado.py
      Escenarios: ESC-B, ESC-EC, ESC-AC
      Depende de: T-02

- [ ] T-06 DTO EstadoPracticasEstudiante
      Archivos: src/aplicacion/seguimiento/estado_practicas_estudiante.py
      Escenarios: ESC-B, ESC-TO
      Depende de: T-05

- [ ] T-07 Caso de uso ConsultarEstadoPractica
      Archivos: src/aplicacion/seguimiento/consultar_estado_practica.py
      Escenarios: todos menos ESC-TV
      Depende de: T-01, T-03, T-04, T-06

## Infraestructura

- [ ] T-08 RepositorioPracticasMemoria: prácticas de un estudiante
      Archivos: src/infraestructura/repositorio_practicas_memoria.py
      Escenarios: ESC-TO
      Depende de: T-01

- [ ] T-09 ControladorRest: consultar_estado (GET /estudiantes/yo/practicas y GET /practicas/{id}/estado)
      Archivos: src/infraestructura/controlador_rest.py
      Escenarios: todos
      Depende de: T-07

## Composición

- [ ] T-10 Composición en main.py con ConsultarEstadoPractica
      Archivos: src/main.py
      Escenarios: todos
      Depende de: T-08, T-09

## Validación

- [ ] T-11 Validar escenario por escenario y registrar la evidencia
      Archivos: specs/010-consultar-estado-practica/validacion.md
      Escenarios: todos
      Depende de: T-10
