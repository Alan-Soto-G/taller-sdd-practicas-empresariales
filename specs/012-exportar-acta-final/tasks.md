# Tareas: 012 Exportar el acta final

Derivadas de [plan.md](plan.md). Una tarea por clase o archivo, de adentro hacia afuera. En los commits se escribe "012 T-NN". Implementadas por Claude sin obreros. Nombres de escenario según [spec.md](spec.md):

| Clave | Escenario |
|-------|-----------|
| ESC-B | Flujo básico - el Coordinador exporta un acta generada por el Worker |
| ESC-ES | Flujo alterno - el Estudiante exporta el acta de su práctica |
| ESC-AP | Flujo alterno - también se exporta un acta aprobada |
| ESC-SP | Excepción - el acta no tiene PDF generado (esquema: en generación, con error) |
| ESC-AN | Excepción - el acta no existe |
| ESC-AJ | EAC-04 - un estudiante intenta exportar el acta de otro |
| ESC-SR | Excepción - un rol que no es actor de CU-12 intenta exportar |
| ESC-AL | Excepción - el Repositorio de actas no tiene el archivo |
| ESC-TV | Excepción - petición con token vencido |

## Aplicación

- [x] T-01 Error ActaNoExportable con su motivo
      Archivos: src/aplicacion/errores/acta_no_exportable.py
      Escenarios: ESC-SP
      Depende de: ninguna

- [x] T-02 DTO SolicitudExportacionActa
      Archivos: src/aplicacion/actas/solicitud_exportacion_acta.py
      Escenarios: todos menos ESC-TV
      Depende de: ninguna

- [ ] T-03 DTO ActaExportada
      Archivos: src/aplicacion/actas/acta_exportada.py
      Escenarios: ESC-B, ESC-ES, ESC-AP
      Depende de: ninguna

- [ ] T-04 Caso de uso ExportarActa
      Archivos: src/aplicacion/actas/exportar_acta.py
      Escenarios: todos menos ESC-TV
      Depende de: T-01, T-02, T-03

## Infraestructura y composición

- [ ] T-05 ControladorRest: exportar_acta (GET /actas/{id}/pdf) con 409 y 503
      Archivos: src/infraestructura/controlador_rest.py
      Escenarios: todos
      Depende de: T-04

- [ ] T-06 Composición en main.py con ExportarActa
      Archivos: src/main.py
      Escenarios: todos
      Depende de: T-05

## Validación

- [ ] T-07 Validar escenario por escenario y registrar la evidencia
      Archivos: specs/012-exportar-acta-final/validacion.md
      Escenarios: todos
      Depende de: T-06
