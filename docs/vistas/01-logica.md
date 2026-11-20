# Vista lógica: modelo de dominio

> Las abstracciones clave del Sistema de Gestión de Prácticas Empresariales. Diagrama: [01-logica.puml](../diagramas/01-logica.puml). Para usuarios finales y analistas. Notación: UML (C4 no tiene un diagrama para esta vista).

## 1. Presentación principal

Muestra los conceptos del negocio y cómo se relacionan, no las clases del código. Son pocas clases, solo con sus atributos clave, sin métodos ni elementos técnicos. Las multiplicidades guardan reglas del negocio: `0..3` intentos de generación es el máximo de reintentos del ADR-001, y `0..3` aprobaciones son las de tutor, empresa y coordinador. Estas abstracciones viven en `dominio/` (entidades de Clean Architecture).

Diagrama: [diagramas/01-logica.puml](../diagramas/01-logica.puml)

## 2. Catálogo de elementos

| Entidad | Qué representa | Atributos clave | Regla del negocio |
|---------|----------------|-----------------|-------------------|
| Estudiante | Quien realiza la práctica | documento, programa, correo institucional | Solo consulta y modifica sus propias postulaciones, horas y práctica (EAC-04) |
| Tutor | Docente que acompaña la práctica | documento, correo institucional | Atiende como máximo la carga definida en ReglaPractica; solo aprueba las horas de sus prácticas asignadas |
| Empresa | Empresa aliada con convenio vigente | NIT, razón social | Solo se gestionan empresas ya aliadas (alcance de la visión) |
| RepresentanteEmpresa | Persona de la empresa que supervisa y evalúa | nombre, correo | No tiene cuenta institucional: accede con un EnlaceAcceso (ADR-005) |
| Plaza | Vacante de práctica que ofrece una empresa | cargo, cupos, periodo | No admite más postulaciones aceptadas que cupos |
| Postulacion | Solicitud de un estudiante a una plaza | fecha, estado | Estados: enviada, aceptada, rechazada; un estudiante tiene a lo sumo una postulación aceptada por periodo |
| Practica | La práctica de un estudiante en una empresa | fecha de inicio, estado, horas aprobadas | Nace de una postulación aceptada; pertenece a un Estudiante; conserva la versión de ReglaPractica con la que empezó (ADR-008) |
| RegistroHoras | Horas reportadas por el estudiante en una semana | semana, horas, actividades, estado | Estados: reportado, aprobado, rechazado; un solo registro por práctica y semana; aprobado no se modifica |
| ReglaPractica | Versión de las reglas del reglamento | versión, horas requeridas, carga máxima por tutor, plantilla del acta | Es un dato, no código: se cambia sin programar (EAC-03) |
| CriterioEvaluacion | Aspecto que la empresa califica | nombre, escala | Es un dato de la ReglaPractica; se agregan criterios sin programar (EAC-03) |
| Evaluacion | Evaluación de desempeño hecha por la empresa | fecha, calificaciones, observaciones | Una por práctica; califica todos los criterios de su ReglaPractica |
| EnlaceAcceso | Enlace de un solo uso para el representante | acción, vencimiento, usado | Vence a los 7 días y se invalida al usarse (ADR-005) |
| ActaFinal | Documento que cierra la práctica | fecha de solicitud, estado, ruta del PDF | Estados: en generación, generada, aprobada, con error; solo se solicita con las horas requeridas aprobadas y la evaluación registrada |
| IntentoGeneracion | Cada intento del Worker de actas de componer el PDF | número, fecha, resultado | Máximo 3 por acta (ADR-001) |
| Aprobacion | Aprobación electrónica que reemplaza la firma manual | rol, usuario, fecha | Tres por acta (tutor, empresa y coordinador); con las tres, el acta queda aprobada (ADR-006) |

Ciclo de vida de la Práctica:

| Estado | Significado | Transiciones válidas |
|--------|-------------|----------------------|
| sin tutor | La postulación fue aceptada y la práctica existe sin tutor asignado | en curso |
| en curso | Tiene tutor asignado y el estudiante registra horas | horas completas |
| horas completas | Las horas aprobadas alcanzan las horas requeridas de su ReglaPractica | evaluada |
| evaluada | La empresa registró la evaluación de desempeño | acta en trámite |
| acta en trámite | Su ActaFinal se está generando o espera aprobaciones | cerrada |
| cerrada | El acta tiene las tres aprobaciones | (final) |

## 3. Justificación

- CU-01, CU-03, CU-04, CU-06 y CU-07: de ellos salen Postulacion, Practica, RegistroHoras, Evaluacion y ActaFinal.
- EAC-02 y ADR-001: IntentoGeneracion deja rastro de cada intento; ningún acta se pierde sin explicación.
- EAC-03 y ADR-008: ReglaPractica y CriterioEvaluacion como datos cumplen el límite de 2 módulos por cambio.
- EAC-04 y ADR-004: toda Practica pertenece a un Estudiante, y solo su tutor asignado aprueba sus horas.
- EAC-05 y ADR-005: EnlaceAcceso le da acceso al RepresentanteEmpresa sin cuenta institucional.
- OB-03 y ADR-006: Aprobacion reemplaza la recolección de firmas manuales.
- OB-02: un solo RegistroHoras por práctica y semana evita duplicados.

## 4. Comportamiento

Los diagramas de secuencia cambian el estado de los conceptos. [CU-01](../diagramas/secuencias/cu01-postularse.puml) crea una Postulacion. [CU-03](../diagramas/secuencias/cu03-asignar-tutor.puml) lleva la Practica a "en curso". [CU-04](../diagramas/secuencias/cu04-registrar-horas.puml) crea un RegistroHoras. [CU-06](../diagramas/secuencias/cu06-evaluar-practicante.puml) usa un EnlaceAcceso y crea la Evaluacion. En [CU-07](../diagramas/secuencias/cu07-generar-acta-final.puml), cada vuelta del loop del worker crea un IntentoGeneracion.

## 5. Vistas relacionadas

- [Desarrollo](03-desarrollo.md): estas entidades viven en `dominio/` y los módulos las usan.
- [Procesos](02-procesos.md): se guardan en PostgreSQL, y el PDF del acta en el Repositorio de actas.

## Diferencia con el diagrama de clases del diseño

El modelo de dominio muestra conceptos del negocio con atributos clave, sin tipos ni métodos, y lo entiende cualquier stakeholder, incluido el Coordinador de Prácticas. El diagrama de clases del diseño se hace al programar e incluye tipos, visibilidad, métodos y los puertos de `aplicacion/`.
