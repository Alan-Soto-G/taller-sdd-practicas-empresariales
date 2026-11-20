# ADR-009: Desplegar en contenedores Docker sobre los servidores de la facultad

## Estado

Aceptado (2026-11-19)

## Contexto

La preocupación PA-06 exige decidir cómo se construye y despliega el sistema. El supuesto S-01 indica que la universidad ya tiene la infraestructura de servidores, y RN-01 impide gastar en hardware o en servicios pagos. Al Líder de Infraestructura TI (visión) le preocupan el consumo de recursos, la facilidad de despliegue y el cumplimiento de las políticas de red. El riesgo R-02 y el escenario [EAC-01](../drivers.md#eac-01-eficiencia-de-desempeño-capacidad) exigen más capacidad en el cierre de semestre. RN-02 exige estar en producción en 4 meses.

## Alternativas consideradas

- **A) Instalación manual en los servidores.** Sin herramientas nuevas; pero cada despliegue es distinto, difícil de repetir y de replicar en el cierre.
- **B) Contenedores Docker (API de prácticas, Worker de actas, broker) orquestados con Docker Compose en los servidores de la facultad.** Despliegue repetible con un solo comando; la API y el worker se replican en el cierre de semestre. Exige que TI opere Docker.
- **C) Plataforma en la nube pública con escalado automático.** Elasticidad real; pero tiene costo recurrente fuera del presupuesto (RN-01) e ignora la infraestructura existente (S-01).

## Decisión

Se elige la opción B, porque usa la infraestructura existente sin costo de licencias (S-01, RN-01) y permite replicar la API y el Worker de actas solo en el cierre (EAC-01, R-02). La aplicación web se sirve como archivos estáticos con Nginx. La base de datos y el broker solo son accesibles desde la red interna de la facultad.

## Consecuencias

### Positivas

- Despliegue repetible y el mismo entorno en desarrollo y en producción.
- La capacidad adicional se agrega solo en temporada de cierre, sin cambiar el código.

### Negativas y costos aceptados

- El equipo de TI debe aprender a operar y monitorear contenedores.
- La réplica es manual (no elástica): alguien debe escalar antes del cierre y reducir después.

### Riesgos asumidos

- Que los servidores existentes no alcancen para el pico (S-01 falso). Mitigación: prueba de carga de EAC-01 antes del primer cierre.

### Vistas que modifica

[Física](../vistas/04-fisica.md) (nodos y contenedores).
