# ADR-012: Leer los archivos de Excel del histórico con openpyxl detrás del puerto LectorExcel

## Estado

Aceptado (2026-11-20). Complementa [ADR-008](ADR-008-reglas-configurables.md).

## Contexto

[ADR-008](ADR-008-reglas-configurables.md) decidió cargar la información inicial (PA-07, S-04) con "un importador de una sola vez (CU-13) que valida los archivos de Excel y reporta las filas rechazadas, sin cargarlas en silencio". No eligió cómo leer los archivos `.xlsx`, y la biblioteca estándar de Python no lee Excel.

La primera versión de CU-13 recibía el libro ya leído (hojas → filas): el Coordinador no podía subir su archivo directamente. Restricciones:
- RN-01: código abierto y sin licencias pagas.
- ADR-002: `aplicacion/` no depende de librerías de infraestructura.
- ADR-007: un archivo ilegible es un error de aplicación.
- ADR-009: imagen Docker liviana.

## Alternativas consideradas

- **A) openpyxl (licencia MIT).** Lee `.xlsx` en Python puro, con una sola dependencia (et_xmlfile, MIT). Su modo `read_only` sirve para archivos grandes. No lee el formato antiguo `.xls`.
- **B) pandas con openpyxl.** Lectura en tablas con poco código; pero agrega pandas y numpy (decenas de MB) para un importador de una sola vez, y su conversión automática de tipos puede alterar datos sin avisar (contradice "sin cargarlas en silencio").
- **C) Pedir a la Coordinación que exporte a CSV.** Sin dependencias; pero cambia el proceso de los usuarios, pierde las varias hojas de un libro y agrega un paso manual propenso a errores de codificación.

## Decisión

Se elige la opción **A, openpyxl 3.1.5**: el Coordinador sube el `.xlsx` tal como lo tiene y no se agregan dependencias pesadas.

La librería queda detrás de un **puerto nuevo, `LectorExcel`**, en `aplicacion/puertos/`: `leer(contenido: bytes) -> dict[str, list[dict[str, str]]]`, que devuelve, por hoja, las filas como textos por encabezado (la fila 1 es el encabezado). Lo implementa `LectorExcelOpenpyxl` en `infraestructura/`.
- Un archivo que no es un `.xlsx` válido se traduce al error de aplicación `ArchivoNoValido` (ADR-007).
- El caso de uso `ImportarHistorico` (Módulo Configuración) autoriza, pide las hojas al puerto, valida cada fila con las reglas del dominio y reporta las rechazadas con su hoja, su fila y su motivo.
- La versión se fija en `src/requirements.txt`.

## Consecuencias

### Positivas

- La Coordinación carga sus hojas actuales sin convertirlas.
- Cambiar de librería solo toca el adaptador.

### Negativas y costos aceptados

- Otra dependencia externa, aunque es de uso único (S-04).
- Los `.xls` antiguos deben guardarse antes como `.xlsx`.

### Riesgos asumidos

- S-04 puede ser falso y los datos venir muy sucios. Mitigación: el reporte de filas rechazadas (ADR-008) permite corregirlas y volver a importar; las filas ya cargadas se rechazan como duplicadas.

### Vistas que modifica

[Desarrollo](../vistas/03-desarrollo.md): el puerto LectorExcel y el Adaptador de Excel (openpyxl); el Módulo Configuración depende también de LectorExcel. Glosario de [arquitectura.md](../arquitectura.md#10-glosario): Lector de Excel.
