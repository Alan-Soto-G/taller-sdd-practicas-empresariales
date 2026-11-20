# Documento de arquitectura: Sistema de Gestión de Prácticas Empresariales

> Versión 1.0 | Estado: completo hasta las vistas y los escenarios (+1). La sección 9 conserva la deuda técnica que se registre durante la implementación.

Este documento es el mapa del proyecto. Enlaza a los demás archivos y no los copia: un dato escrito en dos lugares termina diciendo dos cosas distintas. Su estructura es una adaptación de arc42.

## 1. Introducción y objetivos

El sistema permite que la Facultad de Ingenierías gestione en un solo lugar las prácticas empresariales de 500 estudiantes y 50 tutores al año. Cubre la postulación a plazas, la asignación de tutor, el seguimiento de horas, la evaluación de la empresa y la generación y aprobación electrónica del acta final, y reemplaza las hojas de Excel y el correo electrónico. Los cuatro objetivos de negocio (OB-01 a OB-04) buscan reducir el ciclo de asignación de tutores, las inconsistencias en el registro de horas y el esfuerzo de generar el acta final, y mejorar la satisfacción de las empresas aliadas.

Detalle: [Visión](vision.md)

Funcionalidades: [catálogo de casos de uso](drivers.md#1-casos-de-uso-y-casos-de-uso-primarios) (CU-01 a CU-14), cada uno enlazado a su carpeta de `specs/`.

## 2. Restricciones

Cuatro restricciones: integración con el Directorio Activo / SSO de la universidad (RT-01), aplicativo 100% web y responsivo (RT-02), presupuesto de la vigencia fiscal de la facultad (RN-01) y primera versión en producción en máximo 4 meses (RN-02).

Detalle: [Restricciones](drivers.md#3-restricciones)

## 3. Contexto del sistema

El sistema se relaciona con cuatro personas (Estudiante, Tutor, Coordinador de Prácticas y Representante de la Empresa) y dos sistemas externos (Directorio Activo / SSO y Servicio de correo institucional).

Detalle: [Contexto](contexto.md)

## 4. Estrategia de solución

| Driver | Enfoque | ADR |
|--------|---------|-----|
| EAC-02, EAC-01, R-02, CU-07 | Generación asíncrona del acta final con cola de mensajes, reintentos y cola de errores | [ADR-001](adr/ADR-001-generacion-acta-asincrona.md) |
| PA-01, RN-02, EAC-03 | Monolito modular con Clean Architecture; Worker de actas como proceso aparte | [ADR-002](adr/ADR-002-estructura-general.md) |
| PA-01, RN-01, S-01, EAC-01 | PostgreSQL para el proceso y repositorio institucional para los PDF de las actas | [ADR-003](adr/ADR-003-persistencia.md) |
| RT-01, PA-02, EAC-04 | SSO institucional, token de corta vida y autorización por rol y titularidad | [ADR-004](adr/ADR-004-autenticacion-autorizacion.md) |
| PA-02, EAC-05, RT-02, CU-06 | Enlace de un solo uso y con vencimiento para el Representante de la Empresa | [ADR-005](adr/ADR-005-acceso-representante-empresa.md) |
| PA-04, EAC-04, OB-03 | Auditoría en tabla de PostgreSQL dentro de la transacción; aprobaciones electrónicas en lugar de firmas | [ADR-006](adr/ADR-006-registro-trazabilidad.md) |
| PA-03, EAC-02 | Fallas de integración traducidas a errores de aplicación y respuesta HTTP unificada | [ADR-007](adr/ADR-007-manejo-errores.md) |
| PA-05, PA-07, EAC-03, S-04 | Reglas de la práctica como datos y carga inicial por migraciones e importador de Excel | [ADR-008](adr/ADR-008-reglas-configurables.md) |
| PA-06, S-01, RN-01, R-02 | Contenedores Docker en los servidores de la universidad; réplicas en el cierre de semestre | [ADR-009](adr/ADR-009-despliegue-contenedores.md) |
| RT-02, EAC-05, OB-04 | Aplicación web adaptable de una sola página en Angular | [ADR-010](adr/ADR-010-aplicacion-web-adaptable.md) |
| CU-07, RN-01, DT-05 | PDF del acta con ReportLab detrás del puerto ComponedorActa | [ADR-011](adr/ADR-011-libreria-pdf-actas.md) |
| CU-13, PA-07, S-04, RN-01 | Lectura del histórico en Excel con openpyxl detrás del puerto LectorExcel | [ADR-012](adr/ADR-012-lectura-excel-historico.md) |

## 5. Vistas (4+1)

[Lógica](vistas/01-logica.md) | [Procesos](vistas/02-procesos.md) | [Desarrollo](vistas/03-desarrollo.md) | [Física](vistas/04-fisica.md)

Escenarios (+1): [diagramas/secuencias/](diagramas/secuencias/) y la tabla de escenarios en [drivers.md](drivers.md#6-escenarios-1).

### Matriz de cobertura: drivers y ADR por vista

Ninguna fila vacía: todo driver y todo ADR se ven en al menos una vista.

| Driver o ADR | Contexto (marco) | Lógica | Procesos | Desarrollo | Física |
|--------------|:----------------:|:------:|:--------:|:----------:|:------:|
| CU-01, CU-03, CU-04, CU-06, CU-07 (casos de uso primarios) | ✓ | ✓ | ✓ | ✓ | |
| EAC-01: registro de horas en menos de 2 s en el cierre | | | ✓ | | ✓ |
| EAC-02: ningún acta se pierde | | ✓ | ✓ | | ✓ |
| EAC-03: máximo 2 módulos por cambio del reglamento | | ✓ | | ✓ | |
| EAC-04: acceso ajeno rechazado y registrado | | ✓ | | ✓ | |
| EAC-05: evaluación de la empresa en menos de 5 minutos | ✓ | | ✓ | ✓ | |
| RT-01: Directorio Activo / SSO | ✓ | | ✓ | ✓ | |
| RT-02: 100% web y responsivo | | | ✓ | | ✓ |
| RN-01: presupuesto de la vigencia | | | ✓ | | ✓ |
| RN-02: producción en 4 meses | | | ✓ | ✓ | |
| ADR-001 Generación asíncrona del acta | | ✓ | ✓ | | ✓ |
| ADR-002 Estructura general | | | ✓ | ✓ | |
| ADR-003 Persistencia | | | ✓ | | ✓ |
| ADR-004 Autenticación y autorización | ✓ | | ✓ | ✓ | |
| ADR-005 Acceso del Representante de la Empresa | ✓ | ✓ | | ✓ | |
| ADR-006 Registro y trazabilidad | | ✓ | | ✓ | |
| ADR-007 Manejo de errores | | | | ✓ | |
| ADR-008 Reglas configurables | | ✓ | | ✓ | |
| ADR-009 Despliegue en contenedores | | | | | ✓ |
| ADR-010 Aplicación web adaptable | | | ✓ | | ✓ |
| ADR-011 Librería de PDF del acta | | | ✓ | ✓ | |
| ADR-012 Lectura del histórico en Excel | | | | ✓ | |

Nota: EAC-02 también se ve en el escenario [CU-07](diagramas/secuencias/cu07-generar-acta-final.puml), EAC-04 en [CU-04](diagramas/secuencias/cu04-registrar-horas.puml) y EAC-05 en [CU-06](diagramas/secuencias/cu06-evaluar-practicante.puml). RN-01 se verifica, además, en que todas las tecnologías de los catálogos son de código abierto.

## 6. Conceptos transversales

| Concepto | Cómo se resuelve | Dónde se ve |
|----------|------------------|-------------|
| Autenticación y autorización | SSO institucional con token de corta vida para los usuarios internos; enlace de un solo uso para los representantes; autorización por rol y titularidad en el caso de uso | [ADR-004](adr/ADR-004-autenticacion-autorizacion.md), [ADR-005](adr/ADR-005-acceso-representante-empresa.md), [Desarrollo](vistas/03-desarrollo.md) |
| Manejo de errores | Los adaptadores traducen las fallas a errores de aplicación; respuesta HTTP unificada | [ADR-007](adr/ADR-007-manejo-errores.md) |
| Registro y trazabilidad | Tabla de auditoría; Aprobacion por cada aprobación del acta e IntentoGeneracion por cada intento del worker | [ADR-006](adr/ADR-006-registro-trazabilidad.md), [Lógica](vistas/01-logica.md) |
| Configuración | Reglas de la práctica y criterios de evaluación como datos versionados; secretos en variables de entorno | [ADR-008](adr/ADR-008-reglas-configurables.md) |
| Entorno de construcción y despliegue | Imágenes Docker para la API, el worker y el broker; Nginx para la aplicación web | [ADR-009](adr/ADR-009-despliegue-contenedores.md), [Física](vistas/04-fisica.md) |
| Estructura general | Monolito modular con Clean Architecture y Worker de actas aparte | [ADR-002](adr/ADR-002-estructura-general.md) |
| Migración inicial de datos | Migraciones versionadas e importador de Excel que reporta las filas rechazadas | [ADR-008](adr/ADR-008-reglas-configurables.md) |

## 7. Decisiones de diseño

| ADR | Decisión | Estado | Drivers |
|-----|----------|--------|---------|
| [ADR-001](adr/ADR-001-generacion-acta-asincrona.md) | Generación asíncrona del acta con cola | Aceptado | EAC-01, EAC-02, R-02, CU-07 |
| [ADR-002](adr/ADR-002-estructura-general.md) | Monolito modular con Clean Architecture | Aceptado | RN-02, EAC-03, PA-01 |
| [ADR-003](adr/ADR-003-persistencia.md) | PostgreSQL y repositorio de actas institucional | Aceptado | RN-01, S-01, EAC-01, PA-01 |
| [ADR-004](adr/ADR-004-autenticacion-autorizacion.md) | SSO institucional, token de corta vida y autorización por rol y titularidad | Aceptado | RT-01, EAC-04, PA-02 |
| [ADR-005](adr/ADR-005-acceso-representante-empresa.md) | Enlace de un solo uso para el Representante de la Empresa | Aceptado | RT-01, RT-02, EAC-05, PA-02 |
| [ADR-006](adr/ADR-006-registro-trazabilidad.md) | Auditoría en tabla de PostgreSQL | Aceptado | EAC-04, OB-03, PA-04 |
| [ADR-007](adr/ADR-007-manejo-errores.md) | Errores de aplicación y respuesta unificada | Aceptado | EAC-02, PA-03 |
| [ADR-008](adr/ADR-008-reglas-configurables.md) | Reglas de la práctica como datos | Aceptado | EAC-03, PA-05, PA-07 |
| [ADR-009](adr/ADR-009-despliegue-contenedores.md) | Contenedores Docker | Aceptado | S-01, RN-01, PA-06 |
| [ADR-010](adr/ADR-010-aplicacion-web-adaptable.md) | Aplicación web adaptable | Aceptado | RT-02, EAC-05, OB-04 |
| [ADR-011](adr/ADR-011-libreria-pdf-actas.md) | PDF del acta con ReportLab y puerto ComponedorActa | Aceptado | CU-07, RN-01, EAC-02 |
| [ADR-012](adr/ADR-012-lectura-excel-historico.md) | Histórico en Excel con openpyxl y puerto LectorExcel | Aceptado | CU-13, PA-07, S-04, RN-01 |

Todos los drivers de [drivers.md](drivers.md) quedan cubiertos por al menos un ADR.

## 8. Requisitos de calidad

| EAC | Atributo | Prioridad | ADR | Se verifica en |
|-----|----------|-----------|-----|----------------|
| EAC-01 | Eficiencia de desempeño | Alta | ADR-001, ADR-003, ADR-009 | [specs/004](../specs/004-registrar-horas/spec.md), escenario de carga en el cierre |
| EAC-02 | Fiabilidad | Alta | ADR-001, ADR-007 | [specs/007](../specs/007-generar-acta-final/spec.md), escenarios de reintentos y cola de errores |
| EAC-03 | Mantenibilidad | Media | ADR-002, ADR-008 | Revisión del cambio al agregar un criterio de evaluación (cuenta de módulos tocados) |
| EAC-04 | Seguridad | Alta | ADR-004, ADR-006 | [specs/004](../specs/004-registrar-horas/spec.md), escenario de acceso ajeno; también specs 005, 006, 008 y 010 |
| EAC-05 | Capacidad de interacción | Alta | ADR-005, ADR-010 | [specs/006](../specs/006-evaluar-practicante/spec.md) y prueba de usuario con el 90% en menos de 5 minutos |

Un EAC sin escenario en ninguna spec queda en evidencia: nadie lo está verificando. EAC-03 y la parte de prueba de usuario de EAC-05 se verifican fuera de las specs.

## 9. Riesgos y deuda técnica

| ID | Riesgo o deuda | Origen | Impacto | Respuesta |
|----|----------------|--------|---------|-----------|
| R-01 | Resistencia al cambio de tutores y delegados de empresa, que podrían insistir en el correo | [vision.md](vision.md) | Evaluaciones y aprobaciones fuera del sistema (OB-04) | Acceso sin cuenta ni instalación por enlace desde el correo (ADR-005, ADR-010) |
| R-02 | Colapso en el cierre de semestre por registros de horas de última hora y generación simultánea de actas | [vision.md](vision.md) | Incumplimiento de EAC-01 y EAC-02 | Actas en el worker (ADR-001) y réplicas en el cierre (ADR-009); prueba de carga antes del primer cierre |
| R-03 | Retrasos en la integración con el SSO de TI | [vision.md](vision.md), RT-01 | Compromete el plazo de RN-02 | Puerto ProveedorIdentidad con adaptador simulado mientras TI habilita la integración (ADR-004) |
| R-04 | La cola de actas crece sin control en el cierre | ADR-001 (riesgo asumido) | Retraso en la entrega de actas (OB-03) | Alerta al superar 100 pendientes y réplica temporal del worker |
| DT-01 | Las actas que agotan los 3 intentos quedan en `errores_actas` y dependen del Coordinador | Secuencia de [CU-07](diagramas/secuencias/cu07-generar-acta-final.puml) | Sobrecarga del Coordinador en el cierre | Se acepta en esta etapa; automatizar el reprocesamiento si la cola de errores crece |
| DT-02 | PDF huérfanos si el worker falla entre guardar el archivo y actualizar la base de datos | ADR-003 | Inconsistencia entre almacenes | Proceso periódico de conciliación (pendiente) |
| DT-03 | No hay una política de retención de la auditoría | ADR-006 | Crecimiento de la tabla con cada cohorte | Acordarla con el Coordinador y el DBA antes del primer cierre |
| DT-04 | La seguridad del enlace de un solo uso depende del buzón del representante | ADR-005 | Un tercero con acceso al correo podría evaluar | Vida de 7 días, uso único y auditoría de cada uso |
| DT-05 | La librería de generación de PDF no está decidida | ADR-001 | Bloquea la implementación de CU-07 | **Resuelta** por [ADR-011](adr/ADR-011-libreria-pdf-actas.md): ReportLab (BSD) detrás del puerto ComponedorActa |

## 10. Glosario

| Término | Definición | Nombre en el código |
|---------|------------|---------------------|
| Estudiante | Quien realiza la práctica; solo accede a sus propias postulaciones, horas y práctica | `Estudiante` |
| Tutor | Docente asignado que acompaña la práctica y aprueba las horas | `Tutor` |
| Coordinador de Prácticas | Gestiona plazas, empresas, asignaciones y actas | `CoordinadorPracticas` |
| Empresa | Empresa aliada con convenio vigente | `Empresa` |
| Representante de la Empresa | Supervisor de la empresa que evalúa al practicante y aprueba el acta, sin cuenta institucional | `RepresentanteEmpresa` |
| Plaza | Vacante de práctica que ofrece una empresa, con sus cupos | `Plaza` |
| Postulación | Solicitud de un estudiante a una plaza: enviada, aceptada o rechazada | `Postulacion` |
| Práctica | La práctica de un estudiante en una empresa, desde la postulación aceptada hasta el acta aprobada | `Practica` |
| Estado de la práctica | Sin tutor, en curso, horas completas, evaluada, acta en trámite o cerrada | `EstadoPractica` |
| Registro de horas | Horas reportadas por semana: reportado, aprobado o rechazado | `RegistroHoras` |
| Regla de la práctica | Versión del reglamento: horas requeridas, carga máxima por tutor y plantilla del acta | `ReglaPractica` |
| Criterio de evaluación | Aspecto que la empresa califica | `CriterioEvaluacion` |
| Evaluación | Evaluación de desempeño registrada por la empresa | `Evaluacion` |
| Enlace de acceso | Enlace de un solo uso y con vencimiento para el representante | `EnlaceAcceso` |
| Acta final | Documento que cierra la práctica: en generación, generada, aprobada o con error | `ActaFinal` |
| Intento de generación | Cada intento del Worker de actas de componer el PDF; máximo 3 por acta | `IntentoGeneracion` |
| Aprobación | Aprobación electrónica del acta por tutor, empresa o coordinador; reemplaza la firma manual | `Aprobacion` |
| Proveedor de identidad | Puerto para validar la identidad contra el Directorio Activo / SSO | `ProveedorIdentidad` |
| Repositorio de prácticas | Puerto de persistencia de las entidades del proceso | `RepositorioPracticas` |
| Publicador de actas | Puerto que publica las solicitudes de acta en la cola | `PublicadorActas` |
| Almacén de actas | Puerto para leer y guardar los PDF de las actas | `AlmacenActas` |
| Componedor de actas | Puerto que compone el PDF del acta a partir de sus datos consolidados (ADR-011) | `ComponedorActa` |
| Lector de Excel | Puerto que lee las hojas de un archivo .xlsx como filas por encabezado (ADR-012) | `LectorExcel` |
| Notificador | Puerto para enviar correos y enlaces | `Notificador` |
| Bitácora | Puerto para registrar la auditoría | `Bitacora` |
| Solicitud de acta | Mensaje que la API publica para que el Worker de actas genere un acta | mensaje `SolicitudActa` |
| Cola de actas | Cola del broker donde esperan las solicitudes de acta | cola `actas` |
| Cola de errores de actas | Cola donde quedan las actas que agotaron los intentos | cola `errores_actas` |
