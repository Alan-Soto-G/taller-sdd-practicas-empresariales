# Drivers arquitectónicos: Sistema de Gestión de Prácticas Empresariales

> **Enunciado.** Partiendo de [vision.md](vision.md), se extraen los drivers que moldean la arquitectura: casos de uso primarios, escenarios de atributos de calidad, restricciones y preocupaciones arquitectónicas, más la matriz de priorización y la tabla de escenarios (+1).

## 1. Casos de uso y casos de uso primarios

| ID | Caso de uso | Actor | ¿Primario? | Justificación | Se especifica en |
|----|-------------|-------|------------|---------------|------------------|
| **CU-01** | Postularse a una plaza de práctica | Estudiante | Sí | Importancia para el negocio (inicio del proceso) y alta frecuencia: los 500 estudiantes se postulan en las primeras semanas del periodo | [specs/001](../specs/001-postularse-plaza/spec.md) |
| **CU-02** | Publicar plazas de práctica | Coordinador de Prácticas | No | CRUD estándar sobre empresas ya aliadas | [specs/002](../specs/002-publicar-plazas/spec.md) |
| **CU-03** | Asignar tutor a un estudiante | Coordinador de Prácticas | Sí | Importancia para el negocio (OB-01) y complejidad: reparte 500 estudiantes entre 50 tutores respetando la carga máxima de cada uno | [specs/003](../specs/003-asignar-tutor/spec.md) |
| **CU-04** | Registrar horas de práctica | Estudiante | Sí | Alta frecuencia y riesgo: concentración masiva al cierre del semestre (R-02); ligado a OB-02, EAC-01 y EAC-04 | [specs/004](../specs/004-registrar-horas/spec.md) |
| **CU-05** | Aprobar horas reportadas | Tutor / Docente | No | Cambio de estado sobre registros ya existentes; la integridad se cubre con EAC-04 | [specs/005](../specs/005-aprobar-horas/spec.md) |
| **CU-06** | Evaluar el desempeño del practicante | Representante de la Empresa | Sí | Riesgo y complejidad: actor externo sin cuenta institucional (conflicto con RT-01) que debe evaluar sin instalar nada (RT-02, S-02); ligado a OB-04, EAC-03 y EAC-05 | [specs/006](../specs/006-evaluar-practicante/spec.md) |
| **CU-07** | Generar el acta final | Coordinador de Prácticas (la genera el Worker de actas) | Sí | Importancia para el negocio (OB-03) y riesgo: generación simultánea de actas al cierre (R-02); ligado a EAC-02 | [specs/007](../specs/007-generar-acta-final/spec.md) |
| **CU-08** | Aprobar el acta final | Tutor, Representante de la Empresa y Coordinador de Prácticas | No | Aprobación electrónica sobre un acta ya generada; la trazabilidad se cubre con EAC-04 | [specs/008](../specs/008-aprobar-acta-final/spec.md) |
| **CU-09** | Consultar el avance de los estudiantes asignados | Tutor / Docente | No | Consulta de datos que ya están en el sistema | [specs/009](../specs/009-consultar-avance-tutor/spec.md) |
| **CU-10** | Consultar el estado de la práctica y del acta | Estudiante | No | Consulta simple; la confidencialidad se cubre con EAC-04 | [specs/010](../specs/010-consultar-estado-practica/spec.md) |
| **CU-11** | Generar reportes de prácticas | Coordinador de Prácticas | No | Importante para el negocio, pero no estructura nada: opera sobre datos ya estructurados | [specs/011](../specs/011-generar-reportes/spec.md) |
| **CU-12** | Exportar el acta final | Coordinador de Prácticas o Estudiante | No | Lectura de un archivo ya generado y almacenado | [specs/012](../specs/012-exportar-acta-final/spec.md) |
| **CU-13** | Cargar información histórica desde Excel | Coordinador de Prácticas | No | Operación de una sola vez al arrancar (S-04); se resuelve como preocupación PA-07 | [specs/013](../specs/013-cargar-historico-excel/spec.md) |
| **CU-14** | Gestionar empresas aliadas y sus representantes | Coordinador de Prácticas | No | CRUD estándar; las empresas ya tienen convenio (fuera del alcance de la visión) | [specs/014](../specs/014-gestionar-empresas/spec.md) |

Este catálogo es la lista de funcionalidades del sistema. Cada caso de uso se especifica en la carpeta de `specs/` con su mismo número (CU-03 → `specs/003-...`); un caso de uso sin enlace en "Se especifica en" es una funcionalidad que nadie ha especificado.

## 2. Escenarios de atributos de calidad

### EAC-01: Eficiencia de desempeño (capacidad)

| Parte | Pregunta | Contenido |
|-------|----------|-----------|
| **1. Fuente del estímulo** | ¿Quién o qué lo provoca? | Un estudiante autenticado |
| **2. Estímulo** | ¿Qué ocurre? | Registra las horas de práctica de la semana |
| **3. Artefacto** | ¿Sobre qué parte? | El módulo de horas de la API de prácticas |
| **4. Entorno** | ¿En qué condiciones? | Última semana del semestre (R-02), con hasta 300 usuarios concurrentes y generación de actas en curso |
| **5. Respuesta** | ¿Qué debe hacer el sistema? | Valida el registro, lo guarda como "reportado" y lo confirma al estudiante sin esperar trabajos pesados |
| **6. Medida de respuesta** | ¿Cómo se verifica? | **Confirmación en menos de 2 segundos en el 95% de los casos; 0 registros perdidos o duplicados** |

**Escenario redactado.** Durante la última semana del semestre, con hasta 300 usuarios concurrentes y actas generándose al mismo tiempo, un estudiante autenticado registra sus horas de la semana. El módulo de horas valida y guarda el registro y lo confirma en menos de 2 segundos en el 95% de los casos, sin perder ni duplicar registros.

**Traza:** OB-02, R-02, CU-04

### EAC-02: Fiabilidad (tolerancia a fallos)

| Parte | Pregunta | Contenido |
|-------|----------|-----------|
| **1. Fuente del estímulo** | ¿Quién o qué lo provoca? | El Coordinador de Prácticas |
| **2. Estímulo** | ¿Qué ocurre? | Solicita la generación del acta final de hasta 500 prácticas a la vez y la generación de algunas falla (error al componer el PDF o caída del Worker de actas) |
| **3. Artefacto** | ¿Sobre qué parte? | El Worker de actas y la cola de actas usados por CU-07 |
| **4. Entorno** | ¿En qué condiciones? | Cierre de semestre (R-02), con el registro de horas en operación |
| **5. Respuesta** | ¿Qué debe hacer el sistema? | Acepta la solicitud, deja cada acta en la cola, la genera en segundo plano con hasta 3 intentos y espera creciente entre ellos y, si se agotan los intentos, la deja en la cola de errores para el Coordinador |
| **6. Medida de respuesta** | ¿Cómo se verifica? | **Solicitud aceptada en menos de 3 segundos; 0 actas perdidas; el 100% de las actas termina generada o en la cola de errores; cada acta generada en máximo 10 minutos después de solicitada en el 95% de los casos** |

**Escenario redactado.** Al cierre del semestre, el Coordinador solicita las actas finales de 500 prácticas. El sistema acepta la solicitud en menos de 3 segundos y genera las actas en segundo plano. Si la generación de un acta falla, se intenta hasta 3 veces con espera creciente y, si se agotan los intentos, pasa a la cola de errores. Ningún acta se pierde y el 95% queda generada en máximo 10 minutos.

**Traza:** OB-03, R-02, CU-07

### EAC-03: Mantenibilidad (modificabilidad)

| Parte | Pregunta | Contenido |
|-------|----------|-----------|
| **1. Fuente del estímulo** | ¿Quién o qué lo provoca? | El Coordinador de Prácticas, por un cambio en el reglamento, y un desarrollador del equipo |
| **2. Estímulo** | ¿Qué ocurre? | Hay que cambiar las horas requeridas de la práctica o agregar un criterio al formulario de evaluación de la empresa |
| **3. Artefacto** | ¿Sobre qué parte? | La API de prácticas (módulos de casos de uso y dominio) y la configuración |
| **4. Entorno** | ¿En qué condiciones? | Con el sistema en producción y prácticas en curso |
| **5. Respuesta** | ¿Qué debe hacer el sistema? | Admite el cambio como dato de configuración, sin modificar la lógica de las reglas existentes, y lo aplica a las prácticas nuevas |
| **6. Medida de respuesta** | ¿Cómo se verifica? | **Cambio que toca 2 módulos o menos, en máximo 2 días por persona, sin detener el servicio y sin alterar las prácticas en curso** |

**Escenario redactado.** El reglamento cambia y hay que agregar un criterio al formulario de evaluación de la empresa. Con el sistema en producción, el cambio se hace como dato de configuración, toca no más de 2 módulos, toma máximo 2 días por persona y se aplica sin detener el servicio ni alterar las prácticas en curso.

**Traza:** OB-04, CU-06, stakeholder Arquitecto de Software

### EAC-04: Seguridad (confidencialidad y responsabilidad)

| Parte | Pregunta | Contenido |
|-------|----------|-----------|
| **1. Fuente del estímulo** | ¿Quién o qué lo provoca? | Un usuario autenticado por el SSO institucional |
| **2. Estímulo** | ¿Qué ocurre? | Intenta consultar o modificar las horas, la evaluación o el acta de una práctica que no le pertenece ni tiene asignada |
| **3. Artefacto** | ¿Sobre qué parte? | La API de prácticas (autorización en los casos de uso) y el repositorio de actas |
| **4. Entorno** | ¿En qué condiciones? | Operación normal |
| **5. Respuesta** | ¿Qué debe hacer el sistema? | Rechaza la petición y registra el intento en la bitácora de auditoría |
| **6. Medida de respuesta** | ¿Cómo se verifica? | **El 100% de los intentos de acceso ajeno se rechaza y queda registrado con usuario, recurso y hora** |

**Escenario redactado.** Un estudiante autenticado intenta consultar las horas de otro estudiante. La API rechaza la petición y registra el intento con usuario, recurso y hora. Esto ocurre en el 100% de los intentos.

**Traza:** OB-02, RT-01, CU-04, CU-05, CU-10

### EAC-05: Capacidad de interacción (operabilidad)

| Parte | Pregunta | Contenido |
|-------|----------|-----------|
| **1. Fuente del estímulo** | ¿Quién o qué lo provoca? | Un Representante de la Empresa que accede desde su teléfono móvil |
| **2. Estímulo** | ¿Qué ocurre? | Evalúa por primera vez el desempeño de un practicante, sin ayuda |
| **3. Artefacto** | ¿Sobre qué parte? | La aplicación web (formulario de evaluación) |
| **4. Entorno** | ¿En qué condiciones? | Operación normal, pantalla pequeña, sin cuenta institucional y sin instalar software (S-02) |
| **5. Respuesta** | ¿Qué debe hacer el sistema? | Lo lleva desde el enlace recibido por correo hasta la confirmación de la evaluación enviada |
| **6. Medida de respuesta** | ¿Cómo se verifica? | **Evaluación completada en menos de 5 minutos por el 90% de los representantes de la prueba, sin instalar nada ni crear cuenta** |

**Escenario redactado.** Un Representante de la Empresa abre desde su teléfono el enlace que recibió por correo y evalúa por primera vez a su practicante, sin ayuda. La aplicación web lo guía hasta la confirmación, y el 90% de los representantes de la prueba lo logra en menos de 5 minutos, sin instalar nada ni crear una cuenta.

**Traza:** OB-04, RT-02, S-02, R-01, CU-06

## 3. Restricciones

| ID | Restricción | Tipo | Origen | Impacto arquitectónico esperado |
|----|-------------|------|--------|---------------------------------|
| **RT-01** | Integrarse con el Directorio Activo (o SSO) de la universidad para el inicio de sesión | Técnica | Oficina de TI de la universidad | Obliga a delegar la autenticación de los usuarios internos en un adaptador del SSO (sin credenciales propias); entra en conflicto con los representantes de las empresas, que no tienen cuenta institucional (PA-02) |
| **RT-02** | Aplicativo 100% web y con diseño responsivo para móviles | Técnica | Arquitectura de Software | Descarta aplicaciones nativas o de escritorio; obliga a una aplicación web adaptable servida desde la infraestructura de la facultad (EAC-05) |
| **RN-01** | El desarrollo y despliegue no puede exceder el presupuesto de la vigencia fiscal de la facultad | Negocio | Decanatura de la Facultad de Ingenierías | Orienta a tecnologías de código abierto sin licencias y a reutilizar la infraestructura existente (S-01); descarta servicios pagos de terceros (por ejemplo, firma digital certificada) |
| **RN-02** | Primera versión funcional en producción en máximo 4 meses | Negocio | Coordinación de Prácticas | Descarta microservicios por costo de construcción y operación; obliga a una estructura simple de desarrollar y desplegar (monolito modular) |

## 4. Preocupaciones arquitectónicas

| ID | Preocupación | Qué hay que decidir | Por qué importa en este sistema |
|----|--------------|---------------------|---------------------------------|
| **PA-01** | Estructura general | Cómo se divide el sistema y en cuántos procesos | 4 meses de plazo (RN-02); el cierre de semestre no debe degradar el registro de horas (EAC-01, EAC-02) |
| **PA-02** | Autenticación y autorización | Cómo se identifica a cada rol y cómo accede el Representante de la Empresa sin cuenta institucional | RT-01 cubre a estudiantes, tutores y coordinador, pero no a las empresas; cada práctica solo la ven su titular, su tutor, su representante y el coordinador (EAC-04, EAC-05) |
| **PA-03** | Manejo de errores y excepciones | Estrategia unificada ante fallas del SSO, del correo y de la generación de actas | Ningún acta ni registro de horas se pierde sin explicación (EAC-02) |
| **PA-04** | Registro y trazabilidad | Qué se registra, dónde y por cuánto tiempo | Las aprobaciones de horas y de actas reemplazan las firmas manuales (OB-03) y deben poder probarse; auditoría de accesos rechazados (EAC-04) |
| **PA-05** | Configuración | Cómo se parametrizan las horas requeridas, la carga máxima por tutor, los criterios de evaluación y la plantilla del acta sin recompilar | Cambios del reglamento sin detener el servicio (EAC-03) |
| **PA-06** | Entorno de desarrollo, construcción y despliegue | Cómo se empaqueta y despliega en los servidores de la facultad | Consumo de recursos y políticas de red del Líder de Infraestructura TI; S-01 y RN-01 |
| **PA-07** | Migración inicial de datos | Cómo se cargan las empresas, plazas, tutores y prácticas en curso desde los archivos de Excel actuales | El sistema debe arrancar con la información vigente (S-04); preocupación del DBA por la integridad de los datos |

## 5. Matriz de priorización

### Alta importancia, alta dificultad: atender primero

CU-04, CU-06, CU-07, EAC-01, EAC-02, RT-01, PA-01, PA-02

### Alta importancia, baja dificultad: hacer ya

CU-01, CU-03, EAC-04, EAC-05, RT-02, RN-01, RN-02, PA-04, PA-06

### Baja importancia, baja dificultad: hacer si sobra tiempo

CU-02, CU-05, CU-08, CU-09, CU-10, CU-12, CU-14, EAC-03, PA-03, PA-05

### Baja importancia, alta dificultad: cuestionar

CU-11, CU-13, PA-07

## 6. Escenarios (+1)

Inventario de escenarios que se diagraman. Un escenario sin caso de uso primario o EAC detrás no se diagrama.

| ID | Escenario | Origen | Por qué es escenario | Archivo en secuencias/ |
|----|-----------|--------|----------------------|------------------------|
| **ESC-01** | Postularse a una plaza | CU-01 | Caso de uso primario. Muestra la validación de cupo y elegibilidad antes de registrar la postulación | [cu01-postularse.puml](diagramas/secuencias/cu01-postularse.puml) |
| **ESC-02** | Asignar tutor | CU-03 | Caso de uso primario. Muestra la regla de carga máxima por tutor (PA-05) y la notificación por correo | [cu03-asignar-tutor.puml](diagramas/secuencias/cu03-asignar-tutor.puml) |
| **ESC-03** | Registrar horas | CU-04 | Caso de uso primario. Muestra la confirmación en menos de 2 s (EAC-01) y el rechazo auditado del acceso ajeno (EAC-04) | [cu04-registrar-horas.puml](diagramas/secuencias/cu04-registrar-horas.puml) |
| **ESC-04** | Evaluar al practicante | CU-06 | Caso de uso primario. Acceso por enlace de un solo uso sin cuenta institucional (ADR-005): cubre EAC-05 | [cu06-evaluar-practicante.puml](diagramas/secuencias/cu06-evaluar-practicante.puml) |
| **ESC-05** | Generar el acta final | CU-07 | Caso de uso primario. Generación asíncrona con reintentos y cola de errores (ADR-001): cubre EAC-02 | [cu07-generar-acta-final.puml](diagramas/secuencias/cu07-generar-acta-final.puml) |

EAC-01, EAC-02, EAC-04 y EAC-05 quedan dentro de los cinco casos primarios, así que no hace falta un escenario adicional. EAC-03 (modificabilidad) no tiene comportamiento en ejecución: se verifica con una revisión del cambio, contando los módulos que toca al agregar un criterio de evaluación, por lo que no requiere un diagrama de secuencia propio.
