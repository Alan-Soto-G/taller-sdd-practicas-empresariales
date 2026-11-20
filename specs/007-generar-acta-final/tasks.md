# Tareas: 007 Generar el acta final

Derivadas de [plan.md](plan.md). Una tarea por clase o archivo, de adentro hacia afuera. En los commits se escribe "007 T-NN". Nombres de escenario según [spec.md](spec.md):

| Clave | Escenario |
|-------|-----------|
| ESC-B1 | Flujo básico (1/2) - el Coordinador solicita el acta y la API solo la encola |
| ESC-B2 | Flujo básico (2/2) - el Worker de actas genera el acta |
| ESC-NE | Excepción - la práctica no está evaluada |
| ESC-PN | Excepción - la práctica no existe |
| ESC-SR | Excepción - un usuario sin el rol CoordinadorPracticas solicita actas |
| ESC-TV | Excepción - petición con token vencido |
| ESC-R1 | Flujo alterno - la generación falla una vez y se reintenta después de 1 minuto |
| ESC-R3 | Excepción - la generación falla 3 veces y el acta pasa a la cola de errores |
| ESC-CO | Flujo alterno - el correo de aviso falla |
| ESC-E2 | EAC-02 - 500 actas en el cierre, con fallas, sin perder ninguna |

## Dominio

- [x] T-01 Enum EstadoActa
      Archivos: src/dominio/estado_acta.py
      Escenarios: ESC-B1, ESC-B2, ESC-R3
      Depende de: ninguna

- [x] T-02 Entidad ActaFinal con solicitar, marcar_generada y marcar_con_error
      Archivos: src/dominio/acta_final.py
      Escenarios: ESC-B1, ESC-B2, ESC-R1, ESC-R3, ESC-E2
      Depende de: T-01

- [x] T-03 Entidad IntentoGeneracion con MAX_INTENTOS y espera_tras
      Archivos: src/dominio/intento_generacion.py
      Escenarios: ESC-B2, ESC-R1, ESC-R3, ESC-E2
      Depende de: ninguna

- [x] T-04 Entidad CoordinadorPracticas
      Archivos: src/dominio/coordinador_practicas.py
      Escenarios: ESC-B2
      Depende de: ninguna

- [x] T-05 Practica: solicitar_acta
      Archivos: src/dominio/practica.py
      Escenarios: ESC-B1, ESC-NE
      Depende de: ninguna

## Aplicación: mensaje, errores y puertos

- [x] T-06 Mensaje SolicitudActa
      Archivos: src/aplicacion/actas/solicitud_acta.py
      Escenarios: ESC-B1, ESC-B2, ESC-R1, ESC-R3
      Depende de: ninguna

- [x] T-07 Error AlmacenNoDisponible
      Archivos: src/aplicacion/errores/almacen_no_disponible.py
      Escenarios: ESC-R1, ESC-R3, ESC-E2
      Depende de: ninguna

- [x] T-08 Puerto PublicadorActas
      Archivos: src/aplicacion/puertos/publicador_actas.py
      Escenarios: ESC-B1, ESC-E2
      Depende de: T-06

- [x] T-09 Puerto AlmacenActas
      Archivos: src/aplicacion/puertos/almacen_actas.py
      Escenarios: ESC-B2, ESC-R1, ESC-R3
      Depende de: T-07

- [x] T-10 Puerto RepositorioPracticas: actas, intentos, evaluación y coordinador
      Archivos: src/aplicacion/puertos/repositorio_practicas.py
      Escenarios: todos menos ESC-TV
      Depende de: T-02, T-03, T-04

## Aplicación: Módulo Actas (API)

- [x] T-11 DTO SolicitudGeneracionActas
      Archivos: src/aplicacion/actas/solicitud_generacion_actas.py
      Escenarios: ESC-B1, ESC-SR
      Depende de: ninguna

- [x] T-12 DTO ResultadoSolicitudActa
      Archivos: src/aplicacion/actas/resultado_solicitud_acta.py
      Escenarios: ESC-B1, ESC-NE, ESC-PN
      Depende de: ninguna

- [x] T-13 DTO ActasSolicitadas
      Archivos: src/aplicacion/actas/actas_solicitadas.py
      Escenarios: ESC-B1, ESC-E2
      Depende de: T-12

- [x] T-14 Caso de uso SolicitarActas
      Archivos: src/aplicacion/actas/solicitar_actas.py
      Escenarios: ESC-B1, ESC-NE, ESC-PN, ESC-SR, ESC-E2
      Depende de: T-02, T-05, T-06, T-08, T-10, T-11, T-13

## Aplicación: Módulo Actas (Worker)

- [x] T-15 DTO ResultadoGeneracion
      Archivos: src/aplicacion/actas/resultado_generacion.py
      Escenarios: ESC-B2, ESC-R1, ESC-R3
      Depende de: ninguna

- [ ] T-16 Caso de uso GenerarActa
      Archivos: src/aplicacion/actas/generar_acta.py
      Escenarios: ESC-B2, ESC-R1, ESC-R3, ESC-CO, ESC-E2
      Depende de: T-02, T-03, T-06, T-07, T-09, T-10, T-15

## Infraestructura

- [ ] T-17 Adaptador ColaActasMemoria (colas actas y errores_actas)
      Archivos: src/infraestructura/cola_actas_memoria.py
      Escenarios: ESC-B1, ESC-B2, ESC-R1, ESC-R3, ESC-E2
      Depende de: T-06

- [ ] T-18 Adaptador AlmacenActasMemoria con fallas simuladas
      Archivos: src/infraestructura/almacen_actas_memoria.py
      Escenarios: ESC-B1, ESC-B2, ESC-R1, ESC-R3, ESC-E2
      Depende de: T-07

- [ ] T-19 Adaptador de entrada WorkerActas (consume la cola y reintenta)
      Archivos: src/infraestructura/worker_actas.py
      Escenarios: ESC-B2, ESC-R1, ESC-R3, ESC-CO, ESC-E2
      Depende de: T-16, T-17

- [ ] T-20 RepositorioPracticasMemoria: actas, intentos, evaluación y coordinador
      Archivos: src/infraestructura/repositorio_practicas_memoria.py
      Escenarios: todos menos ESC-TV
      Depende de: T-10

- [ ] T-21 ControladorRest: solicitar_actas (POST /actas) con 202
      Archivos: src/infraestructura/controlador_rest.py
      Escenarios: ESC-B1, ESC-NE, ESC-PN, ESC-SR, ESC-TV, ESC-E2
      Depende de: T-14

## Composición

- [ ] T-22 Composición de la API en main.py con SolicitarActas y los datos de los Antecedentes
      Archivos: src/main.py
      Escenarios: todos
      Depende de: T-17, T-18, T-20, T-21

- [ ] T-23 Composición del Worker de actas en worker.py
      Archivos: src/worker.py
      Escenarios: ESC-B2, ESC-R1, ESC-R3, ESC-CO, ESC-E2
      Depende de: T-16, T-19

## Validación

- [ ] T-24 Validar escenario por escenario y registrar la evidencia
      Archivos: specs/007-generar-acta-final/validacion.md
      Escenarios: todos
      Depende de: T-22, T-23
