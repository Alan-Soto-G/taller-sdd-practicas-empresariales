# Tareas: 014 Gestionar empresas aliadas y sus representantes

Derivadas de [plan.md](plan.md). Una tarea por clase o archivo, de adentro hacia afuera. En los commits se escribe "014 T-NN". Implementadas por Claude sin obreros. Nombres de escenario según [spec.md](spec.md):

| Clave | Escenario |
|-------|-----------|
| ESC-B | Flujo básico - el Coordinador registra una empresa y su representante |
| ESC-LI | Flujo alterno - el Coordinador lista las empresas con su representante |
| ESC-AC | Flujo alterno - el Coordinador actualiza la razón social y el NIT |
| ESC-CO | Flujo alterno - el correo actualizado del representante recibe los enlaces nuevos |
| ESC-EL | Flujo alterno - se elimina una empresa sin plazas ni prácticas |
| ESC-EP | Excepción - no se elimina una empresa con plazas o prácticas |
| ESC-YE | Excepción - el id de la empresa ya existe |
| ESC-DI | Excepción - los datos no son válidos (esquema) |
| ESC-EN | Excepción - la empresa no existe |
| ESC-SR | Excepción - un usuario sin el rol CoordinadorPracticas gestiona empresas |
| ESC-TV | Excepción - petición con token vencido |

## Dominio

- [x] T-01 Empresa: NIT y motivo_invalidez
      Archivos: src/dominio/empresa.py
      Escenarios: ESC-B, ESC-AC, ESC-DI
      Depende de: ninguna

- [x] T-02 RepresentanteEmpresa: motivo_invalidez
      Archivos: src/dominio/representante_empresa.py
      Escenarios: ESC-B, ESC-CO, ESC-DI
      Depende de: ninguna

## Aplicación

- [x] T-03 Error EmpresaNoValida con su motivo
      Archivos: src/aplicacion/errores/empresa_no_valida.py
      Escenarios: ESC-DI
      Depende de: ninguna

- [x] T-04 Error EmpresaNoPermitida con su motivo
      Archivos: src/aplicacion/errores/empresa_no_permitida.py
      Escenarios: ESC-EP, ESC-YE
      Depende de: ninguna

- [x] T-05 Puerto RepositorioPracticas: empresas, plazas y representantes
      Archivos: src/aplicacion/puertos/repositorio_practicas.py
      Escenarios: ESC-B, ESC-LI, ESC-CO, ESC-EL, ESC-EP
      Depende de: ninguna

- [x] T-06 DTO SolicitudEmpresa
      Archivos: src/aplicacion/postulaciones/solicitud_empresa.py
      Escenarios: ESC-B, ESC-AC, ESC-EL, ESC-EP, ESC-YE, ESC-DI, ESC-EN, ESC-SR
      Depende de: ninguna

- [x] T-07 DTO SolicitudRepresentante
      Archivos: src/aplicacion/postulaciones/solicitud_representante.py
      Escenarios: ESC-B, ESC-CO, ESC-DI
      Depende de: ninguna

- [x] T-08 DTO EmpresaGestionada
      Archivos: src/aplicacion/postulaciones/empresa_gestionada.py
      Escenarios: ESC-B, ESC-LI, ESC-AC, ESC-CO
      Depende de: ninguna

- [x] T-09 Caso de uso GestionarEmpresas
      Archivos: src/aplicacion/postulaciones/gestionar_empresas.py
      Escenarios: todos menos ESC-TV
      Depende de: T-01 a T-08

## Infraestructura y composición

- [x] T-10 RepositorioPracticasMemoria: empresas, plazas y representantes
      Archivos: src/infraestructura/repositorio_practicas_memoria.py
      Escenarios: ESC-B, ESC-LI, ESC-CO, ESC-EL, ESC-EP
      Depende de: T-05

- [ ] T-11 ControladorRest: CRUD de empresas y representante
      Archivos: src/infraestructura/controlador_rest.py
      Escenarios: todos
      Depende de: T-09

- [ ] T-12 Composición en main.py con GestionarEmpresas y el NIT de EMP-ACME
      Archivos: src/main.py
      Escenarios: todos
      Depende de: T-10, T-11

## Validación

- [ ] T-13 Validar escenario por escenario y registrar la evidencia
      Archivos: specs/014-gestionar-empresas/validacion.md
      Escenarios: todos
      Depende de: T-12
