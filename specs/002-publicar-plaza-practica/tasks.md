# Tareas: 002 Publicar plazas de práctica

Derivadas de [plan.md](plan.md). Una tarea por clase o archivo, de adentro hacia afuera. La numeración es propia de esta carpeta; en los commits se escribe "002 T-NN" para no confundirla con las tareas de 001. Nombres de escenario según [spec.md](spec.md):

| Clave | Escenario |
|-------|-----------|
| ESC-B | Flujo básico - el Coordinador publica una plaza |
| ESC-PO | Flujo alterno - un Estudiante se postula a la plaza recién publicada (CU-01) |
| ESC-DU | Flujo alterno - se publica otra plaza igual de la misma empresa en el mismo periodo |
| ESC-EN | Excepción - la empresa no existe |
| ESC-DI | Excepción - los datos de la plaza no son válidos (esquema: cupos 0 y -1, cargo vacío, periodo 2026-3 y 2026) |
| ESC-SR | Excepción - un usuario sin el rol CoordinadorPracticas intenta publicar una plaza |
| ESC-TV | Excepción - petición con token vencido |

## Dominio

- [x] T-01 Entidad Empresa (id y razón social)
      Archivos: src/dominio/empresa.py
      Escenarios: ESC-B, ESC-EN
      Depende de: ninguna

- [x] T-02 Regla de validación Plaza.motivo_invalidez (cargo, cupos, periodo)
      Archivos: src/dominio/plaza.py
      Escenarios: ESC-B, ESC-DI
      Depende de: ninguna

## Aplicación: errores (ADR-007)

- [x] T-03 Error EmpresaNoEncontrada
      Archivos: src/aplicacion/errores/empresa_no_encontrada.py
      Escenarios: ESC-EN
      Depende de: ninguna

- [x] T-04 Error PlazaNoValida con su motivo
      Archivos: src/aplicacion/errores/plaza_no_valida.py
      Escenarios: ESC-DI
      Depende de: ninguna

## Aplicación: DTO y puertos

- [x] T-05 Puerto RepositorioPracticas: obtener_empresa y guardar_plaza
      Archivos: src/aplicacion/puertos/repositorio_practicas.py
      Escenarios: ESC-B, ESC-PO, ESC-DU, ESC-EN
      Depende de: T-01

- [x] T-06 DTO de entrada SolicitudPublicacionPlaza
      Archivos: src/aplicacion/postulaciones/solicitud_publicacion_plaza.py
      Escenarios: ESC-B, ESC-SR
      Depende de: ninguna

- [x] T-07 DTO de salida PlazaPublicada
      Archivos: src/aplicacion/postulaciones/plaza_publicada.py
      Escenarios: ESC-B, ESC-DU
      Depende de: ninguna

## Aplicación: caso de uso

- [x] T-08 Caso de uso PublicarPlaza
      Archivos: src/aplicacion/postulaciones/publicar_plaza.py
      Escenarios: ESC-B, ESC-PO, ESC-DU, ESC-EN, ESC-DI, ESC-SR
      Depende de: T-01, T-02, T-03, T-04, T-05, T-06, T-07

## Infraestructura: adaptadores

- [x] T-09 RepositorioPracticasMemoria: empresas, obtener_empresa, guardar_plaza y listar_plazas
      Archivos: src/infraestructura/repositorio_practicas_memoria.py
      Escenarios: ESC-B, ESC-PO, ESC-DU, ESC-EN
      Depende de: T-05

- [ ] T-10 ControladorRest: publicar_plaza (POST /plazas) con 201, 400 y 404
      Archivos: src/infraestructura/controlador_rest.py
      Escenarios: ESC-B, ESC-EN, ESC-DI, ESC-SR, ESC-TV
      Depende de: T-08

## Composición

- [ ] T-11 Composición en main.py con PublicarPlaza y los datos de los Antecedentes
      Archivos: src/main.py
      Escenarios: todos
      Depende de: T-09, T-10

## Validación

- [ ] T-12 Validar escenario por escenario y registrar la evidencia
      Archivos: specs/002-publicar-plaza-practica/validacion.md
      Escenarios: todos (ESC-B, ESC-PO, ESC-DU, ESC-EN, ESC-DI, ESC-SR, ESC-TV)
      Depende de: T-11
