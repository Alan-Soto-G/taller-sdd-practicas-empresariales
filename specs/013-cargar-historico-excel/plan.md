# Plan: 013 Cargar información histórica desde Excel

Aterriza [spec.md](spec.md) (CU-13) en la arquitectura de [docs/arquitectura.md](../../docs/arquitectura.md). No agrega componentes fuera de [vistas/03-desarrollo.md](../../docs/vistas/03-desarrollo.md) ni librerías sin ADR.

## Decisiones que aplican

| ID | Qué aplica a CU-13 |
|----|--------------------|
| ADR-008 | El importador de una sola vez valida y **reporta las filas rechazadas** sin cargarlas en silencio. Las prácticas importadas usan la ReglaPractica vigente (`ConsultarReglaVigente`, de CU-03). |
| ADR-002 | El caso de uso vive en el **Módulo Configuración** (`src/aplicacion/configuracion/`), que la vista asigna al importador de CU-13. |
| ADR-004 | Solo `CoordinadorPracticas`; autorización en el caso de uso. |
| ADR-006 | Se auditan la creación de cada Práctica importada, el resumen de la importación y el acceso rechazado. |
| ADR-007 | Los rechazos por datos no son errores HTTP: van en el reporte (200). |
| ADR-012 | El `.xlsx` lo lee **openpyxl 3.1.5** detrás del puerto `LectorExcel` (adaptador `LectorExcelOpenpyxl`). Un archivo ilegible → `ArchivoNoValido` (422). La primera versión recibía el libro ya leído; ese camino se conserva. Ajuste: tareas T-11 a T-19. |

## Componentes

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `src/dominio/correo.py` **(nuevo)** | `Correo` | `es_valido(texto) -> bool` (staticmethod): un `@`, con usuario y dominio con punto. Lo reutiliza CU-14 |
| `src/aplicacion/puertos/repositorio_practicas.py` **(cambia)** | `RepositorioPracticas` | Agrega `guardar_empresa`, `guardar_tutor` y `guardar_estudiante` |
| `src/aplicacion/configuracion/solicitud_importacion.py` **(nuevo)** | `SolicitudImportacion` (DTO) | `usuario`, `hojas: dict[str, list[dict[str, str]]]` |
| `src/aplicacion/configuracion/fila_rechazada.py` **(nuevo)** | `FilaRechazada` (DTO) | `hoja`, `fila`, `motivo` |
| `src/aplicacion/configuracion/resultado_importacion.py` **(nuevo)** | `ResultadoImportacion` (DTO) | `cargadas: dict[str, int]`, `rechazadas: tuple[FilaRechazada, ...]` |
| `src/aplicacion/configuracion/importar_historico.py` **(nuevo)** | `ImportarHistorico` | Caso de uso (ver Flujo). Recibe repositorio, bitacora, `ConsultarReglaVigente` y reloj |
| `src/infraestructura/repositorio_practicas_memoria.py` **(cambia)** | `RepositorioPracticasMemoria` | Los tres `guardar_*` |
| `src/infraestructura/controlador_rest.py` **(cambia)** | `ControladorRest` | `importar_historico(token, cuerpo)` representa "POST /importaciones/historico" con `hojas`; 200 con `cargadas` y `rechazadas` |
| `src/main.py` **(cambia)** | (composición) | Crea `ImportarHistorico` |

## Flujo

1. El controlador valida el token (401 si falla).
2. `ImportarHistorico.ejecutar(SolicitudImportacion)`:
   1. Rol distinto de Coordinador → bitácora (`importacion`, "importar histórico") y `AccesoDenegado`.
   2. Una hoja que no es de las cinco conocidas → `FilaRechazada(hoja, 1, "hoja desconocida")`.
   3. Recorre las hojas en el orden Empresas, Plazas, Tutores, Estudiantes, Practicas. Cada fila (número `índice + 2`) se valida:
      - campos obligatorios presentes;
      - id no existente;
      - referencias existentes;
      - cupos enteros y `Plaza.motivo_invalidez`;
      - `Correo.es_valido`.
   4. Si la fila es válida, se guarda. Si es una Practica: `EN_CURSO`, con la versión vigente y el registro en la bitácora.
   5. Registra en la bitácora el resumen ("importar histórico: N cargadas, M rechazadas") y devuelve `ResultadoImportacion`.

## Fuera de alcance

- Importar postulaciones, horas, evaluaciones o actas históricas, y deshacer una importación.

## Ajuste ADR-012 (subir el archivo .xlsx)

| Archivo | Clase | Responsabilidad |
|---------|-------|-----------------|
| `src/aplicacion/errores/archivo_no_valido.py` **(nuevo)** | `ArchivoNoValido` | código `archivo_no_valido`, mensaje "archivo no válido", con `motivo` |
| `src/aplicacion/puertos/lector_excel.py` **(nuevo)** | `LectorExcel` (Protocol) | `leer(contenido: bytes) -> dict[str, list[dict[str, str]]]`; lanza `ArchivoNoValido` |
| `src/aplicacion/configuracion/solicitud_importacion_excel.py` **(nuevo)** | `SolicitudImportacionExcel` (DTO) | `usuario`, `contenido: bytes` |
| `src/aplicacion/configuracion/importar_historico.py` **(cambia)** | `ImportarHistorico` | Recibe también el `LectorExcel`. `ejecutar_excel(SolicitudImportacionExcel)`: autoriza primero (sin leer el archivo si se rechaza), lee las hojas con el puerto y aplica las mismas reglas de `ejecutar` |
| `src/infraestructura/lector_excel_openpyxl.py` **(nuevo)** | `LectorExcelOpenpyxl` | `openpyxl.load_workbook(BytesIO, read_only=True, data_only=True)`; la fila 1 es el encabezado; las celdas pasan a texto (un decimal entero, como 3.0, se lee "3"); se quitan las filas vacías del final; cualquier excepción → `ArchivoNoValido("el archivo no es un Excel .xlsx válido")` |
| `src/infraestructura/controlador_rest.py` **(cambia)** | `ControladorRest` | `importar_historico_excel(token, contenido)` representa "POST /importaciones/historico/archivo" (multipart con el .xlsx); 422 `ArchivoNoValido` con motivo |
| `src/main.py` **(cambia)** | (composición) | Inyecta `LectorExcelOpenpyxl()` en `ImportarHistorico` |
| `src/requirements.txt` **(cambia)** | — | Agrega `openpyxl==3.1.5` |
