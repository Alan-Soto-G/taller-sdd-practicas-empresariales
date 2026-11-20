# ADR-006: Registrar la auditoría en una tabla de PostgreSQL dentro de la misma transacción

## Estado

Aceptado (2026-11-19)

## Contexto

La preocupación PA-04 exige decidir qué se registra y dónde. Las aprobaciones electrónicas de horas (CU-05) y del acta final (CU-08) reemplazan la recolección de firmas manuales (OB-03), así que deben poder probarse después: quién aprobó, qué y cuándo. El escenario [EAC-04](../drivers.md#eac-04-seguridad-confidencialidad-y-responsabilidad) exige que cada acceso rechazado quede registrado con usuario, recurso y hora. OB-02 busca reducir las inconsistencias en el registro de horas, lo que requiere saber quién cambió cada registro.

## Alternativas consideradas

- **A) Tabla de auditoría en PostgreSQL, escrita en la misma transacción del cambio.** Si el cambio se guarda, su registro también; se consulta con SQL. Agrega una escritura a cada transacción.
- **B) Auditoría asíncrona por la cola de mensajes.** Menos latencia por petición; pero un registro puede perderse o llegar tarde si el broker falla, y una aprobación sin rastro no sirve como firma.
- **C) Archivos de log del servidor.** Sin costo de base de datos; pero difíciles de consultar y de conservar, y no garantizan que cada cambio quede registrado.

## Decisión

Se elige la opción A, porque una aprobación que reemplaza una firma (OB-03) no puede quedar sin registro, y la misma transacción lo garantiza. Se audita cada cambio de estado de Postulación, Práctica, RegistroHoras, Evaluación y ActaFinal, cada Aprobación y cada acceso rechazado (EAC-04), con usuario, rol, recurso, acción y hora. Los casos de uso escriben a través del puerto `Bitacora`.

## Consecuencias

### Positivas

- Cada aprobación del acta y de las horas tiene un rastro verificable, que es la base de la aprobación electrónica.
- El Coordinador y el soporte pueden reconstruir la historia de una práctica.

### Negativas y costos aceptados

- Cada transacción hace una escritura más (unos milisegundos), lo que suma en el pico de cierre (EAC-01).
- La tabla crece con cada cohorte; requiere una política de retención.

### Riesgos asumidos

- DT-03: no hay una política de retención definida. Mitigación: acordarla con el Coordinador y el DBA antes del primer cierre.

### Vistas que modifica

[Desarrollo](../vistas/03-desarrollo.md) (Adaptador de bitácora) y [Lógica](../vistas/01-logica.md) (Aprobación).
