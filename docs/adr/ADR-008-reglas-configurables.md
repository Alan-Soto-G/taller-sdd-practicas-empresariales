# ADR-008: Manejar las reglas de la práctica como datos y cargar la información inicial con migraciones

## Estado

Aceptado (2026-11-19)

## Contexto

El escenario [EAC-03](../drivers.md#eac-03-mantenibilidad-modificabilidad) exige que un cambio del reglamento (horas requeridas, carga máxima por tutor, criterios de evaluación o plantilla del acta) toque 2 módulos o menos y se aplique sin detener el servicio. La preocupación PA-05 pide parametrizar el sistema sin recompilar. PA-07 y el supuesto S-04 exigen cargar desde los archivos de Excel actuales las empresas, plazas, tutores y prácticas en curso. El DBA (visión) se preocupa por un modelo apto para migraciones futuras.

## Alternativas consideradas

- **A) Reglas escritas en el código.** Simple al inicio; pero cada cambio del reglamento exige programar, probar y desplegar (incumple EAC-03).
- **B) Reglas como datos versionados en PostgreSQL (ReglaPractica, que incluye horas requeridas, carga máxima por tutor y plantilla del acta, y CriterioEvaluacion) y carga inicial por migraciones versionadas con un importador de Excel.** El Coordinador cambia la regla como dato; cada práctica conserva la versión con la que empezó. Exige validar los datos de configuración.
- **C) Archivos de configuración en el servidor.** Sin cambios de esquema; pero cambiarlos exige acceso al servidor y reiniciar, y no queda historial de versiones.

## Decisión

Se elige la opción B, porque cumple EAC-03 sin despliegues y conserva la versión de las reglas de cada práctica en curso. La carga inicial se hace con migraciones de esquema versionadas, más un importador de una sola vez (CU-13) que valida los archivos de Excel y reporta las filas rechazadas, sin cargarlas en silencio. Los secretos (credenciales del SSO y del correo) van en variables de entorno, nunca en la base de datos.

## Consecuencias

### Positivas

- Un criterio nuevo de evaluación o un cambio de horas requeridas es un dato, no código.
- Las prácticas en curso no cambian de reglas a mitad del periodo.

### Negativas y costos aceptados

- Más tablas y validaciones de configuración en el dominio.
- El importador de Excel es código de un solo uso que hay que mantener hasta el arranque.

### Riesgos asumidos

- S-04 puede ser falso y los Excel requerir limpieza extrema. Mitigación: el importador reporta las filas rechazadas para que el Coordinador las corrija antes del arranque.

### Vistas que modifica

[Lógica](../vistas/01-logica.md) (ReglaPractica y CriterioEvaluacion) y [Desarrollo](../vistas/03-desarrollo.md) (Módulo Configuración).
