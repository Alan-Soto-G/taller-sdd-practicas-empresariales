# ADR-001: Generar el acta final de forma asíncrona con una cola de mensajes

## Estado

Aceptado (2026-11-19)

## Contexto

Al cierre del semestre el Coordinador de Prácticas solicita las actas finales de hasta 500 prácticas casi al mismo tiempo. En esas mismas semanas los estudiantes registran sus horas de última hora (R-02). Generar un acta implica consolidar horas aprobadas, evaluación de la empresa y aprobaciones, y componer un PDF, un trabajo pesado frente a una petición web normal. El escenario [EAC-02](../drivers.md#eac-02-fiabilidad-tolerancia-a-fallos) exige que ningún acta se pierda si su generación falla y que la solicitud se acepte en menos de 3 s. [EAC-01](../drivers.md#eac-01-eficiencia-de-desempeño-capacidad) exige que el registro de horas siga respondiendo en menos de 2 s mientras tanto. Caso de uso involucrado: CU-07. Objetivo de negocio: OB-03.

## Alternativas consideradas

- **A) Generación sincrónica dentro de la petición.** Simple y sin infraestructura adicional; pero 500 actas en la misma API ocupan sus procesos, incumplen EAC-01 y, si la petición se corta, el acta no queda generada ni registrada (incumple EAC-02).
- **B) Cola de mensajes con un worker y reintentos.** La API registra la solicitud de cada acta y la deja en una cola; un proceso en segundo plano (Worker de actas) la genera, reintenta si falla y, si agota los intentos, la deja en una cola de errores. Cumple ambos escenarios; agrega un broker de mensajes que hay que operar.
- **C) Tarea programada nocturna (lote).** No compite con el registro de horas; pero el Coordinador espera hasta el día siguiente, lo que se aleja de la meta de menos de 4 horas por estudiante de OB-03, y un fallo del lote afecta todas las actas de la noche.

## Decisión

Se elige la opción B, porque es la única que cumple EAC-01 y EAC-02 sin retrasar las actas un día entero. La API responde de inmediato con el acta en estado "en generación". El Worker de actas hace hasta 3 intentos con espera creciente entre ellos (1 y 2 min) y, si se agotan los intentos, envía la solicitud a la cola de errores para que la revise el Coordinador. La API nunca genera el PDF: solo encola. El broker es RabbitMQ (código abierto, RN-01) con colas persistentes: `actas` para el trabajo pendiente y `errores_actas` para los intentos agotados. La librería para componer el PDF debe ser de código abierto (RN-01); su elección concreta se registra en un ADR nuevo cuando se planee CU-07.

## Consecuencias

### Positivas

- Se cumplen EAC-01 y EAC-02: el pico de actas no degrada el registro de horas y ningún acta se pierde sin explicación.
- El Worker de actas se puede replicar por separado en el cierre de semestre (ADR-009).

### Negativas y costos aceptados

- Se introduce un broker de mensajes que el Líder de Infraestructura TI debe operar y monitorear.
- La experiencia del Coordinador pasa de "generar y descargar" a "solicitar y esperar notificación", y eso debe comunicarse con claridad en la interfaz.
- Las actas que agotan los intentos dependen de la revisión manual del Coordinador (DT-01 en [arquitectura.md](../arquitectura.md#9-riesgos-y-deuda-técnica)).

### Riesgos asumidos

- R-04: si la cola de actas crece sin control al cierre, las actas se demoran. Mitigación: alerta al superar 100 elementos pendientes y réplica temporal del worker.

### Vistas que modifica

[Procesos](../vistas/02-procesos.md) (broker y Worker de actas), [Física](../vistas/04-fisica.md) (servidor de mensajería), [Lógica](../vistas/01-logica.md) (IntentoGeneración) y la secuencia [CU-07](../diagramas/secuencias/cu07-generar-acta-final.puml).
