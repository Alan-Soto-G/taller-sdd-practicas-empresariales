# ADR-011: Componer el PDF del acta final con ReportLab detrás del puerto ComponedorActa

## Estado

Aceptado (2026-11-20). Complementa [ADR-001](ADR-001-generacion-acta-asincrona.md) y resuelve la deuda técnica DT-05.

## Contexto

[ADR-001](ADR-001-generacion-acta-asincrona.md) decidió que el Worker de actas compone el PDF del acta final y dejó pendiente la librería: "debe ser de código abierto (RN-01); su elección concreta se registra en un ADR nuevo cuando se planee CU-07". Esa decisión pendiente quedó como DT-05 en [arquitectura.md](../arquitectura.md#9-riesgos-y-deuda-técnica). Ahora se implementa CU-07 y hace falta una librería real.

Restricciones que aplican:
- RN-01: código abierto y sin licencias pagas.
- RN-02: algo simple de integrar en el plazo.
- [ADR-009](ADR-009-despliegue-contenedores.md): imágenes Docker livianas.
- [ADR-002](ADR-002-estructura-general.md): Clean Architecture, es decir que `aplicacion/` no puede depender de una librería de infraestructura.
- EAC-02 y [ADR-007](ADR-007-manejo-errores.md): una falla al componer debe convertirse en un error de aplicación para que el Worker reintente.

El acta contiene datos de la práctica, horas aprobadas y requeridas, la tabla de calificaciones de la evaluación, la plantilla de su ReglaPractica (ADR-008) y el espacio de las tres aprobaciones electrónicas (CU-08).

## Alternativas consideradas

- **A) ReportLab (licencia BSD).** Librería madura para generar PDF en Python. En Python 3.15 se instala desde una sola wheel `py3-none-any`, y sus dependencias (Pillow y charset-normalizer) también son abiertas. Su API de lienzo (`canvas`) basta para un documento de una página. La API de alto nivel (Platypus) es más extensa de aprender.
- **B) fpdf2 (licencia LGPL-3.0).** API simple, de Python puro. Arrastra fontTools, y la licencia LGPL obliga a revisar las condiciones de redistribución en las imágenes Docker.
- **C) WeasyPrint (HTML a PDF, licencia BSD).** Permite usar la plantilla como HTML. Necesita librerías nativas (Pango, Cairo y GTK), que agrandan la imagen del Worker y complican el despliegue en Windows para el desarrollo.

## Decisión

Se elige la opción **A, ReportLab 5.1.0**, porque es abierta con licencia permisiva (RN-01), se instala sin dependencias nativas (ADR-009) y cubre el acta de una página con su API de lienzo.

Para no romper la regla de dependencia (ADR-002), la librería queda detrás de un **puerto nuevo, `ComponedorActa`**, en `aplicacion/puertos/`: `componer(datos: DatosActa) -> bytes`. Lo implementa el adaptador `ComponedorActaReportlab` en `infraestructura/`.
- El caso de uso `GenerarActa` del Módulo Actas consolida los datos en el DTO `DatosActa` y pide el PDF al puerto.
- El adaptador traduce cualquier falla de la librería al error de aplicación `ActaNoComponible` (ADR-007). El Worker lo cuenta como un `IntentoGeneracion` fallido y reintenta (ADR-001).
- Solo el Worker de actas compone el puerto con su adaptador. La API nunca lo recibe (ADR-001).
- La versión se fija en `src/requirements.txt` (`reportlab==5.1.0`).

## Consecuencias

### Positivas

- DT-05 queda resuelta y CU-07 produce actas en PDF reales.
- Cambiar de librería solo toca el adaptador: `aplicacion/` y `dominio/` no conocen ReportLab.
- La falla al componer, que aparece en la secuencia de CU-07, tiene su propio error de aplicación y entra en los reintentos.

### Negativas y costos aceptados

- Primera dependencia externa del proyecto: hay que mantener su versión en `src/requirements.txt` y en la imagen del Worker.
- El diseño del acta se escribe con coordenadas en el adaptador. La plantilla de la ReglaPractica (ADR-008) se registra en el acta por su nombre, pero el diseño visual todavía no es un dato configurable.

### Riesgos asumidos

- Si la Coordinación pide plantillas visuales editables sin programar (EAC-03), habrá que pasar a plantillas como datos (por ejemplo, Platypus con estilos guardados o HTML). Mitigación: el puerto `ComponedorActa` permite cambiar el adaptador sin tocar los casos de uso.

### Vistas que modifica

[Desarrollo](../vistas/03-desarrollo.md): el puerto ComponedorActa y el Adaptador PDF (ReportLab), y el Módulo Actas depende también de ComponedorActa. [Procesos](../vistas/02-procesos.md): el Worker de actas compone el PDF con ReportLab. Glosario de [arquitectura.md](../arquitectura.md#10-glosario): Componedor de actas.
