# ADR-007: Traducir las fallas de integración a errores de aplicación con una respuesta HTTP unificada

## Estado

Aceptado (2026-11-19)

## Contexto

La preocupación PA-03 exige una estrategia unificada ante fallas del SSO institucional, del Servicio de correo, del almacenamiento de actas y de la base de datos. El escenario [EAC-02](../drivers.md#eac-02-fiabilidad-tolerancia-a-fallos) exige que ningún acta se pierda sin explicación. Clean Architecture (ADR-002) impide que el dominio conozca las excepciones de las librerías de infraestructura.

## Alternativas consideradas

- **A) Cada módulo maneja sus errores a su manera.** Sin diseño previo; pero las respuestas al usuario son inconsistentes y las excepciones técnicas se filtran a los casos de uso.
- **B) Los adaptadores traducen las fallas técnicas a errores de aplicación, y el controlador los convierte en una respuesta HTTP unificada.** Los casos de uso solo conocen errores propios (por ejemplo, `IdentidadNoDisponible`, `CorreoNoEnviado`, `AccesoDenegado`); exige definir el catálogo de errores.
- **C) Reintentos automáticos genéricos en todas las llamadas.** Oculta las fallas transitorias; pero reintentar operaciones que no son idempotentes puede duplicar registros de horas (contradice EAC-01).

## Decisión

Se elige la opción B, porque mantiene el dominio libre de detalles técnicos (ADR-002) y da una respuesta predecible al usuario. Los reintentos se aplican solo donde son seguros: en el Worker de actas (ADR-001) y en el envío de correos. Un correo que no se pudo enviar no revierte la operación principal: queda registrado para reenvío.

## Consecuencias

### Positivas

- Respuestas uniformes (código, mensaje y identificador de correlación) que el soporte puede rastrear.
- Cambiar una librería de infraestructura no toca los casos de uso.

### Negativas y costos aceptados

- Hay que mantener el catálogo de errores de aplicación y su traducción en cada adaptador.

### Riesgos asumidos

- Que un adaptador nuevo no traduzca sus errores y filtre excepciones técnicas. Mitigación: se revisa en la validación arquitectónica de cada funcionalidad.

### Vistas que modifica

[Desarrollo](../vistas/03-desarrollo.md) (Controlador REST y adaptadores).
