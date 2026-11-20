# Tareas: 011 Generar reportes de prácticas

Derivadas de [plan.md](plan.md). Una tarea por clase o archivo, de adentro hacia afuera. En los commits se escribe "011 T-NN". Implementadas por Claude sin obreros. Nombres de escenario según [spec.md](spec.md):

| Clave | Escenario |
|-------|-----------|
| ESC-B | Flujo básico - el Coordinador genera el reporte general |
| ESC-CA | Flujo alterno - el reporte refleja los cambios del proceso |
| ESC-EM | Flujo alterno - reporte filtrado por empresa |
| ESC-EN | Excepción - la empresa del filtro no existe |
| ESC-SR | Excepción - un usuario sin el rol CoordinadorPracticas genera el reporte |
| ESC-TV | Excepción - petición con token vencido |

## Aplicación

- [x] T-01 Puerto RepositorioPracticas: listar_practicas
      Archivos: src/aplicacion/puertos/repositorio_practicas.py
      Escenarios: ESC-B, ESC-CA, ESC-EM
      Depende de: ninguna

- [x] T-02 DTO SolicitudReporte
      Archivos: src/aplicacion/seguimiento/solicitud_reporte.py
      Escenarios: todos menos ESC-TV
      Depende de: ninguna

- [x] T-03 DTO ReportePracticas
      Archivos: src/aplicacion/seguimiento/reporte_practicas.py
      Escenarios: ESC-B, ESC-CA, ESC-EM
      Depende de: ninguna

- [x] T-04 Caso de uso GenerarReporte
      Archivos: src/aplicacion/seguimiento/generar_reporte.py
      Escenarios: todos menos ESC-TV
      Depende de: T-01, T-02, T-03

## Infraestructura y composición

- [x] T-05 ControladorRest: generar_reporte (GET /reportes/practicas)
      Archivos: src/infraestructura/controlador_rest.py
      Escenarios: todos
      Depende de: T-04

- [x] T-06 Composición en main.py con GenerarReporte
      Archivos: src/main.py
      Escenarios: todos
      Depende de: T-05

## Validación

- [ ] T-07 Validar escenario por escenario y registrar la evidencia
      Archivos: specs/011-generar-reportes/validacion.md
      Escenarios: todos
      Depende de: T-06
