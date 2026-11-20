# Tareas: 008 Aprobar el acta final

Derivadas de [plan.md](plan.md). Una tarea por clase o archivo, de adentro hacia afuera. En los commits se escribe "008 T-NN". Nombres de escenario según [spec.md](spec.md):

| Clave | Escenario |
|-------|-----------|
| ESC-B1 | Flujo básico (1/3) - el Tutor asignado aprueba el acta |
| ESC-B2 | Flujo básico (2/3) - el Coordinador emite el enlace de aprobación y el Representante aprueba |
| ESC-B3 | Flujo básico (3/3) - la tercera aprobación cierra la práctica |
| ESC-DO | Excepción - el mismo rol aprueba dos veces |
| ESC-NG | Excepción - el acta no está generada (esquema: en generación, con error) |
| ESC-AN | Excepción - el acta no existe |
| ESC-AJ | EAC-04 - un tutor que no está asignado intenta aprobar el acta |
| ESC-ES | Excepción - el Estudiante titular intenta aprobar su acta |
| ESC-SR | Excepción - un usuario sin el rol CoordinadorPracticas solicita el enlace de aprobación |
| ESC-EN | Excepción - el enlace no sirve para aprobar (esquema: acción evaluar, usado, vencido) |
| ESC-TV | Excepción - petición con token vencido |

## Dominio

- [x] T-01 Entidad Aprobacion con APROBACIONES_REQUERIDAS
      Archivos: src/dominio/aprobacion.py
      Escenarios: ESC-B1, ESC-B2, ESC-B3, ESC-DO
      Depende de: ninguna

- [x] T-02 ActaFinal: aprobar
      Archivos: src/dominio/acta_final.py
      Escenarios: ESC-B3
      Depende de: ninguna

- [x] T-03 Practica: cerrar
      Archivos: src/dominio/practica.py
      Escenarios: ESC-B3
      Depende de: ninguna

## Aplicación

- [x] T-04 Error ActaNoEncontrada
      Archivos: src/aplicacion/errores/acta_no_encontrada.py
      Escenarios: ESC-AN
      Depende de: ninguna

- [x] T-05 Error AprobacionNoPermitida con su motivo
      Archivos: src/aplicacion/errores/aprobacion_no_permitida.py
      Escenarios: ESC-DO, ESC-NG
      Depende de: ninguna

- [x] T-06 Puerto RepositorioPracticas: aprobaciones y acta de una práctica
      Archivos: src/aplicacion/puertos/repositorio_practicas.py
      Escenarios: todos menos ESC-TV
      Depende de: T-01

- [x] T-07 DTO SolicitudEnlaceAprobacion
      Archivos: src/aplicacion/actas/solicitud_enlace_aprobacion.py
      Escenarios: ESC-B2, ESC-SR
      Depende de: ninguna

- [ ] T-08 Caso de uso EmitirEnlaceAprobacion
      Archivos: src/aplicacion/actas/emitir_enlace_aprobacion.py
      Escenarios: ESC-B2, ESC-SR, ESC-EN
      Depende de: T-04, T-05, T-06, T-07

- [ ] T-09 DTO SolicitudAprobacionActa
      Archivos: src/aplicacion/actas/solicitud_aprobacion_acta.py
      Escenarios: ESC-B1, ESC-B3, ESC-AJ, ESC-ES
      Depende de: ninguna

- [ ] T-10 DTO AprobacionRegistrada
      Archivos: src/aplicacion/actas/aprobacion_registrada.py
      Escenarios: ESC-B1, ESC-B2, ESC-B3
      Depende de: ninguna

- [ ] T-11 Caso de uso AprobarActa (con token y con enlace)
      Archivos: src/aplicacion/actas/aprobar_acta.py
      Escenarios: ESC-B1, ESC-B2, ESC-B3, ESC-DO, ESC-NG, ESC-AN, ESC-AJ, ESC-ES, ESC-EN
      Depende de: T-01, T-02, T-03, T-04, T-05, T-06, T-09, T-10

## Infraestructura

- [ ] T-12 RepositorioPracticasMemoria: aprobaciones y acta de una práctica
      Archivos: src/infraestructura/repositorio_practicas_memoria.py
      Escenarios: todos menos ESC-TV
      Depende de: T-06

- [ ] T-13 ControladorRest: emitir_enlace_aprobacion, aprobar_acta y aprobar_acta_con_enlace
      Archivos: src/infraestructura/controlador_rest.py
      Escenarios: todos
      Depende de: T-08, T-11

## Composición

- [ ] T-14 Composición en main.py con el Módulo Actas (CU-08) y los datos de los Antecedentes
      Archivos: src/main.py
      Escenarios: todos
      Depende de: T-12, T-13

## Validación

- [ ] T-15 Validar escenario por escenario y registrar la evidencia
      Archivos: specs/008-aprobar-acta-final/validacion.md
      Escenarios: todos
      Depende de: T-14
