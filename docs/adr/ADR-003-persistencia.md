# ADR-003: Persistir en PostgreSQL y guardar las actas en un repositorio de archivos institucional

## Estado

Aceptado (2026-11-19)

## Contexto

El Administrador de Base de Datos (visión) exige integridad en las transacciones concurrentes de 500 estudiantes y un modelo eficiente para migraciones futuras. Las relaciones son fuertes: estudiante, plaza, postulación, práctica, tutor, horas, evaluación y acta. El escenario [EAC-01](../drivers.md#eac-01-eficiencia-de-desempeño-capacidad) exige 0 registros de horas perdidos o duplicados en el pico de cierre (R-02), y OB-02 busca reducir las inconsistencias en un 95%. El presupuesto no admite licencias (RN-01), y la infraestructura de la universidad ya existe (S-01). Las actas finales son archivos PDF que deben conservarse y exportarse (CU-12).

## Alternativas consideradas

- **A) PostgreSQL para los datos del proceso y un repositorio de archivos institucional para los PDF de las actas.** Modelo relacional con transacciones, claves foráneas y restricciones de unicidad que impiden duplicados; código abierto. Hay que mantener la consistencia entre dos almacenes.
- **B) Base de datos documental (por ejemplo, MongoDB).** Esquema flexible; pero las relaciones entre práctica, tutor, horas y acta se resuelven en la aplicación, y la integridad que pide el DBA queda sin garantía del motor.
- **C) Motor comercial (por ejemplo, SQL Server u Oracle).** Relacional y robusto; pero exige licencias que RN-01 no permite.
- **D) Guardar los PDF dentro de PostgreSQL.** Un solo almacén; pero infla la base de datos, encarece los respaldos y la hace crecer con cada cohorte de 500 actas.

## Decisión

Se elige la opción A, porque cumple la integridad que exigen el DBA y EAC-01 con un motor relacional de código abierto (RN-01), y mantiene la base de datos liviana. Los PDF de las actas se guardan en el almacenamiento de la infraestructura de la universidad (S-01), y en PostgreSQL solo queda su ruta. En esta etapa del taller se usan adaptadores en memoria que implementan los mismos puertos.

## Consecuencias

### Positivas

- Restricciones de unicidad (por ejemplo, un registro de horas por práctica y semana) y claves foráneas que el motor garantiza.
- Respaldos de la base de datos pequeños; los PDF se respaldan con la política del almacenamiento institucional.

### Negativas y costos aceptados

- Dos almacenes que hay que mantener consistentes.
- Requiere migraciones de esquema versionadas (ADR-008).

### Riesgos asumidos

- DT-02: si el worker falla entre guardar el PDF y actualizar la base de datos, queda un archivo huérfano. Mitigación: conciliación periódica (pendiente).

### Vistas que modifica

[Procesos](../vistas/02-procesos.md) (PostgreSQL y Repositorio de actas) y [Física](../vistas/04-fisica.md) (servidor de base de datos y almacenamiento institucional).
