# ADR-002: Estructurar el sistema como un monolito modular con Clean Architecture y un worker aparte

## Estado

Aceptado (2026-11-19)

## Contexto

La preocupación PA-01 exige decidir cómo se divide el sistema. La primera versión debe estar en producción en máximo 4 meses (RN-02), con un presupuesto limitado (RN-01). El escenario [EAC-03](../drivers.md#eac-03-mantenibilidad-modificabilidad) exige que un cambio del reglamento toque 2 módulos o menos. ADR-001 ya separa la generación de actas en un proceso propio. El Arquitecto de Software (visión) se preocupa por la escalabilidad del sistema en el cierre de semestre (R-02).

## Alternativas consideradas

- **A) Microservicios (postulaciones, horas, evaluación, actas).** Cada servicio escala y se despliega por separado; pero multiplica repositorios, despliegues, bases de datos y fallas de red, lo que es inviable en 4 meses (RN-02) y costoso de operar (RN-01).
- **B) Monolito modular con Clean Architecture (API de prácticas) más el Worker de actas como proceso aparte.** Un solo despliegue para la API, con un módulo por caso de uso y capas `dominio/`, `aplicacion/` e `infraestructura/`; el worker comparte el código del dominio. Simple de construir, probar y desplegar; escala todo o nada, salvo el worker.
- **C) Aplicación en capas tradicional (controlador con acceso directo a la base de datos).** Lo más rápido de empezar; pero la lógica queda atada a la base de datos y a la web, y un cambio del reglamento toca muchos archivos (incumple EAC-03).

## Decisión

Se elige la opción B, porque es la única abarcable en 4 meses (RN-02) que cumple EAC-03. El backend se escribe en Python, código abierto y sin licencias (RN-01). La regla de dependencia apunta hacia adentro: `dominio/` no importa nada de `aplicacion/` ni de `infraestructura/`; los puertos se definen en `aplicacion/puertos/` y los implementan los adaptadores de `infraestructura/`.

## Consecuencias

### Positivas

- Desarrollo, pruebas y depuración simples; transacciones locales en una sola base de datos.
- Los módulos se pueden repartir entre los integrantes del equipo sin pisarse.
- Separar más adelante un módulo como servicio es posible porque ya está aislado detrás de puertos.

### Negativas y costos aceptados

- La API escala todo o nada: si solo el registro de horas necesita más capacidad, se replica la API completa (ADR-009).
- Más clases y archivos que un diseño en capas directo; cada capa agrega un salto marginal.

### Riesgos asumidos

- Que los módulos se acoplen con el tiempo (dependencias cíclicas). Mitigación: la vista de usos prohíbe ciclos y se revisa en cada cambio.

### Vistas que modifica

[Desarrollo](../vistas/03-desarrollo.md) (componentes y capas) y [Procesos](../vistas/02-procesos.md) (API de prácticas y Worker de actas).
