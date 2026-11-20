# Tareas: 006 Evaluar el desempeño del practicante

Derivadas de [plan.md](plan.md). Una tarea por clase o archivo, de adentro hacia afuera. En los commits se escribe "006 T-NN". Nombres de escenario según [spec.md](spec.md):

| Clave | Escenario |
|-------|-----------|
| ESC-B1 | Flujo básico (1/3) - el Coordinador emite el enlace de evaluación |
| ESC-B2 | Flujo básico (2/3) - el Representante abre el enlace y ve el formulario |
| ESC-B3 | Flujo básico (3/3) - el Representante envía la evaluación |
| ESC-HC | Excepción - la práctica no tiene las horas completas |
| ESC-SR | Excepción - un usuario sin el rol CoordinadorPracticas solicita la evaluación |
| ESC-TV | Excepción - petición del Coordinador con token vencido |
| ESC-RE | Flujo alterno - el Coordinador reemite el enlace e invalida el anterior |
| ESC-CO | Flujo alterno - el correo del enlace falla |
| ESC-EV | Excepción - el enlace está vencido, usado o es inválido (esquema) |
| ESC-CI | Excepción - las calificaciones no son válidas (esquema) |
| ESC-E5 | EAC-05 - el Representante evalúa sin cuenta ni instalación |
| ESC-E3 | EAC-03 - un criterio nuevo se agrega como dato, sin cambiar código |

## Dominio

- [x] T-01 Entidad CriterioEvaluacion
      Archivos: src/dominio/criterio_evaluacion.py
      Escenarios: ESC-B2, ESC-CI, ESC-E3
      Depende de: ninguna

- [x] T-02 ReglaPractica: criterios
      Archivos: src/dominio/regla_practica.py
      Escenarios: ESC-B2, ESC-CI, ESC-E3
      Depende de: T-01

- [x] T-03 Entidad RepresentanteEmpresa
      Archivos: src/dominio/representante_empresa.py
      Escenarios: ESC-B1, ESC-CO
      Depende de: ninguna

- [x] T-04 Entidad EnlaceAcceso con emitir, motivo_rechazo y usar
      Archivos: src/dominio/enlace_acceso.py
      Escenarios: ESC-B1, ESC-B3, ESC-RE, ESC-EV
      Depende de: ninguna

- [x] T-05 Entidad Evaluacion con motivo_invalidez
      Archivos: src/dominio/evaluacion.py
      Escenarios: ESC-B3, ESC-CI
      Depende de: ninguna

- [x] T-06 Practica: evaluar
      Archivos: src/dominio/practica.py
      Escenarios: ESC-B3
      Depende de: ninguna

## Aplicación: identidad, errores y puertos

- [x] T-07 DTO IdentidadEnlace
      Archivos: src/aplicacion/identidad_enlace.py
      Escenarios: ESC-B2, ESC-B3, ESC-E5
      Depende de: ninguna

- [x] T-08 Error EnlaceNoValido con su motivo
      Archivos: src/aplicacion/errores/enlace_no_valido.py
      Escenarios: ESC-RE, ESC-EV
      Depende de: ninguna

- [x] T-09 Error EvaluacionNoPermitida con su motivo
      Archivos: src/aplicacion/errores/evaluacion_no_permitida.py
      Escenarios: ESC-HC
      Depende de: ninguna

- [ ] T-10 Error EvaluacionNoValida con su motivo
      Archivos: src/aplicacion/errores/evaluacion_no_valida.py
      Escenarios: ESC-CI
      Depende de: ninguna

- [ ] T-11 Puerto RepositorioPracticas: representantes, enlaces y evaluaciones
      Archivos: src/aplicacion/puertos/repositorio_practicas.py
      Escenarios: todos menos ESC-TV
      Depende de: T-03, T-04, T-05

## Aplicación: Módulo Configuración

- [ ] T-12 DTO CriterioConsultado
      Archivos: src/aplicacion/configuracion/criterio_consultado.py
      Escenarios: ESC-B2, ESC-E3
      Depende de: ninguna

- [ ] T-13 Caso de uso ConsultarCriteriosEvaluacion
      Archivos: src/aplicacion/configuracion/consultar_criterios_evaluacion.py
      Escenarios: ESC-B2, ESC-B3, ESC-CI, ESC-E3
      Depende de: T-02, T-11, T-12

## Aplicación: Módulo Evaluación

- [ ] T-14 DTO SolicitudEnlaceEvaluacion
      Archivos: src/aplicacion/evaluacion/solicitud_enlace_evaluacion.py
      Escenarios: ESC-B1, ESC-SR
      Depende de: ninguna

- [ ] T-15 DTO EnlaceEmitido
      Archivos: src/aplicacion/evaluacion/enlace_emitido.py
      Escenarios: ESC-B1, ESC-RE, ESC-CO
      Depende de: ninguna

- [ ] T-16 Caso de uso EmitirEnlaceEvaluacion
      Archivos: src/aplicacion/evaluacion/emitir_enlace_evaluacion.py
      Escenarios: ESC-B1, ESC-HC, ESC-SR, ESC-RE, ESC-CO
      Depende de: T-04, T-09, T-11, T-14, T-15

- [ ] T-17 DTO FormularioEvaluacion
      Archivos: src/aplicacion/evaluacion/formulario_evaluacion.py
      Escenarios: ESC-B2, ESC-E3
      Depende de: T-12

- [ ] T-18 Caso de uso ConsultarFormularioEvaluacion
      Archivos: src/aplicacion/evaluacion/consultar_formulario_evaluacion.py
      Escenarios: ESC-B2, ESC-E5, ESC-E3
      Depende de: T-07, T-13, T-17

- [ ] T-19 DTO SolicitudEvaluacion
      Archivos: src/aplicacion/evaluacion/solicitud_evaluacion.py
      Escenarios: ESC-B3, ESC-CI
      Depende de: T-07

- [ ] T-20 DTO EvaluacionRegistrada
      Archivos: src/aplicacion/evaluacion/evaluacion_registrada.py
      Escenarios: ESC-B3
      Depende de: ninguna

- [ ] T-21 Caso de uso RegistrarEvaluacion
      Archivos: src/aplicacion/evaluacion/registrar_evaluacion.py
      Escenarios: ESC-B3, ESC-CI, ESC-E5
      Depende de: T-05, T-06, T-08, T-09, T-10, T-11, T-13, T-19, T-20

## Infraestructura

- [ ] T-22 Adaptador de entrada ValidadorEnlace
      Archivos: src/infraestructura/validador_enlace.py
      Escenarios: ESC-B2, ESC-B3, ESC-RE, ESC-EV, ESC-E5
      Depende de: T-04, T-07, T-08, T-11

- [ ] T-23 RepositorioPracticasMemoria: representantes, enlaces y evaluaciones
      Archivos: src/infraestructura/repositorio_practicas_memoria.py
      Escenarios: todos menos ESC-TV
      Depende de: T-11

- [ ] T-24 ControladorRest: emitir_enlace_evaluacion, abrir_evaluacion y enviar_evaluacion
      Archivos: src/infraestructura/controlador_rest.py
      Escenarios: todos
      Depende de: T-16, T-18, T-21, T-22

## Composición

- [ ] T-25 Composición en main.py con el Módulo Evaluación y los datos de los Antecedentes
      Archivos: src/main.py
      Escenarios: todos
      Depende de: T-23, T-24

## Validación

- [ ] T-26 Validar escenario por escenario y registrar la evidencia
      Archivos: specs/006-evaluar-practicante/validacion.md
      Escenarios: todos
      Depende de: T-25
