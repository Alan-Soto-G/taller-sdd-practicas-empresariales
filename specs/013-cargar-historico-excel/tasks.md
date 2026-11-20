# Tareas: 013 Cargar información histórica desde Excel

Derivadas de [plan.md](plan.md). Una tarea por clase o archivo, de adentro hacia afuera. En los commits se escribe "013 T-NN". Implementadas por Claude sin obreros. Nombres de escenario según [spec.md](spec.md):

| Clave | Escenario |
|-------|-----------|
| ESC-B | Flujo básico - se importa un libro válido |
| ESC-RE | Flujo alterno - las filas inválidas se reportan y las válidas se cargan |
| ESC-DO | Flujo alterno - importar dos veces el mismo libro no duplica datos |
| ESC-HD | Excepción - el libro tiene una hoja desconocida |
| ESC-SR | Excepción - un usuario sin el rol CoordinadorPracticas importa |
| ESC-TV | Excepción - petición con token vencido |

## Dominio

- [x] T-01 Valor Correo con es_valido
      Archivos: src/dominio/correo.py
      Escenarios: ESC-B, ESC-RE
      Depende de: ninguna

## Aplicación

- [x] T-02 Puerto RepositorioPracticas: guardar_empresa, guardar_tutor y guardar_estudiante
      Archivos: src/aplicacion/puertos/repositorio_practicas.py
      Escenarios: ESC-B, ESC-RE, ESC-DO
      Depende de: ninguna

- [x] T-03 DTO SolicitudImportacion
      Archivos: src/aplicacion/configuracion/solicitud_importacion.py
      Escenarios: todos menos ESC-TV
      Depende de: ninguna

- [x] T-04 DTO FilaRechazada
      Archivos: src/aplicacion/configuracion/fila_rechazada.py
      Escenarios: ESC-RE, ESC-DO, ESC-HD
      Depende de: ninguna

- [x] T-05 DTO ResultadoImportacion
      Archivos: src/aplicacion/configuracion/resultado_importacion.py
      Escenarios: ESC-B, ESC-RE, ESC-DO, ESC-HD
      Depende de: T-04

- [x] T-06 Caso de uso ImportarHistorico
      Archivos: src/aplicacion/configuracion/importar_historico.py
      Escenarios: todos menos ESC-TV
      Depende de: T-01, T-02, T-03, T-05

## Infraestructura y composición

- [x] T-07 RepositorioPracticasMemoria: guardar_empresa, guardar_tutor y guardar_estudiante
      Archivos: src/infraestructura/repositorio_practicas_memoria.py
      Escenarios: ESC-B, ESC-RE, ESC-DO
      Depende de: T-02

- [x] T-08 ControladorRest: importar_historico (POST /importaciones/historico)
      Archivos: src/infraestructura/controlador_rest.py
      Escenarios: todos
      Depende de: T-06

- [x] T-09 Composición en main.py con ImportarHistorico
      Archivos: src/main.py
      Escenarios: todos
      Depende de: T-07, T-08

## Validación

- [ ] T-10 Validar escenario por escenario y registrar la evidencia
      Archivos: specs/013-cargar-historico-excel/validacion.md
      Escenarios: todos
      Depende de: T-09
