# Validación: 013 Cargar información histórica desde Excel

Fecha: 2026-11-20. Código validado: `src/` en el commit `e29dda2` (013 T-18, ajuste de ADR-012); la primera versión se validó en el commit `5feeedf` (013 T-09). Implementado por Claude sin obreros.

Método: cada escenario se ejecutó contra la composición real de `src/main.py` (`construir()`), con una aplicación nueva por escenario. El libro de Excel se pasa ya leído (hojas → filas por encabezado), como decidió la spec. El script con los libros de prueba está en el Anexo. Se ejecuta con `python -B validar_cu13.py <ruta>/src [ruta del .xlsx de muestra]`.

## Validación funcional

| Escenario | Resultado | Evidencia |
|-----------|-----------|-----------|
| ESC-B Libro válido | Cumple | `HTTP 200 {'cargadas': {'Empresas': 1, 'Plazas': 1, 'Tutores': 1, 'Estudiantes': 1, 'Practicas': 1}, 'rechazadas': []}`. Cargados: `Empresa('EMP-H1', 'Histórica S.A.')`, `Plaza('PL-H1', 'EMP-H1', 'Analista', 3, '2026-2')`, `Tutor('T-H1', …)`, `Estudiante('E-H1', …)`, y PR-H1 `('en curso', 'T-H1', 'v1')`. Bitácora: `('C-01', 'practica:PR-H1', 'crear con estado en curso por importación')`, `('C-01', 'importacion', 'importar histórico: 5 cargadas, 0 rechazadas')`. Código: `src/aplicacion/configuracion/importar_historico.py` |
| ESC-RE Filas inválidas reportadas (ADR-008) | Cumple | Cargadas: 1 de cada hoja. 8 rechazadas: Empresas fila 3 `ya existe empresa EMP-ACME`; fila 4 `falta el campo razon_social`; Plazas fila 3 `la empresa EMP-99 no existe`; fila 4 `los cupos deben ser un número entero`; fila 5 `los cupos deben ser mayores que cero`; Tutores fila 3 `el correo no es válido`; Practicas fila 3 `el estudiante E-99 no existe`; fila 4 `el tutor T-99 no existe`. Ninguna rechazada quedó cargada (`[None×7]`) y EMP-ACME conserva su razón social. Código: `importar_historico.py` (`_cargar`), `src/dominio/correo.py`, `src/dominio/plaza.py` (`motivo_invalidez`) |
| ESC-DO Importar dos veces | Cumple | Segunda importación: 0 cargadas y 5 rechazadas: `ya existe empresa EMP-H1`, `ya existe plaza PL-H1`, `ya existe tutor T-H1`, `ya existe estudiante E-H1`, `ya existe práctica PR-H1` |
| ESC-HD Hoja desconocida | Cumple | `'rechazadas': [{'hoja': 'Notas', 'fila': 1, 'motivo': 'hoja desconocida'}]` |
| ESC-SR Sin rol Coordinador (T-500) | Cumple | `HTTP 403`; nada cargado. Bitácora `{'usuario': 'T-500', 'rol': 'Tutor', 'recurso': 'importacion', 'accion': 'importar histórico', 'hora': …}` |
| ESC-TV Token de hace 16 minutos | Cumple | `HTTP 401`; nada cargado |
| ESC-XL Subir el .xlsx (ADR-012) | Cumple | Un archivo `.xlsx` real de 7239 bytes (empieza con `PK`), con las filas de ESC-RE, los cupos como número (3 → 3.0 en Excel) y una fila vacía al final de cada hoja. `HTTP 200` con las mismas cargadas (1 por hoja) y las mismas 8 rechazadas, con su hoja, su fila y su motivo. El resultado es igual al del libro ya leído: `True`. Cupos de PL-H1: `3`. Código: `src/infraestructura/lector_excel_openpyxl.py`, `src/aplicacion/configuracion/importar_historico.py` (`ejecutar_excel`) |
| ESC-AN Archivo que no es Excel | Cumple | `HTTP 422 {'codigo': 'archivo_no_valido', 'mensaje': 'archivo no válido', …, 'motivo': 'el archivo no es un Excel .xlsx válido'}`; nada cargado. Código: `lector_excel_openpyxl.py` (traduce la excepción, ADR-007) |
| ESC-XS Sin rol Coordinador al subir el archivo | Cumple | `HTTP 403`; nada cargado. Bitácora `('T-500', 'importacion', 'importar histórico')`; se rechaza antes de leer el archivo (`ejecutar_excel` → `_autorizar`) |

## Validación arquitectónica

- **Regla de dependencia: cumple.** `src/dominio/correo.py` solo importa `re`; `aplicacion/` no importa `infraestructura/`.
- **Vista de desarrollo: cumple.** El importador está en el Módulo Configuración, como dice la vista. Usa `ConsultarReglaVigente`, del mismo módulo, y no usa otros módulos.
- **ADR:**
  - ADR-008: valida y reporta cada fila rechazada sin cargarla, y las prácticas toman la regla vigente.
  - ADR-004: rol Coordinador.
  - ADR-006: creación de cada práctica, resumen de la importación y rechazo de acceso.
  - ADR-012: openpyxl solo se importa en `src/infraestructura/lector_excel_openpyxl.py`; `aplicacion/` usa el puerto `LectorExcel`, y la versión está fijada en `src/requirements.txt`.
- **Convenciones de AGENTS.md: cumplen.** Una clase por archivo, sin `__init__.py`, sin BOM, DTO en la entrada y la salida.

### Observaciones

1. **CU-01 a CU-12 no se rompieron.** Los scripts de los Anexos dan los mismos códigos: CU-01 `201, 409, 409, 201, 409, 409, 201, 404, 403, 401, [201, 201]`; CU-02 `201×3, 404, 400×5, 403, 401`; CU-03 `200×9, 404, 403, 401`; CU-04 `201, 201, 422×8, 404, 403, 403, 401, {201: 300}`; CU-05 `200×4, 422×3, 404, 403, 403, 401`; CU-06 `201, 200, 201, 409, 403, 401, 410, 200, 201, 410×3, 422×4`; CU-07 `202×3, 403, 401, 202` con 500 de 500 actas; CU-08 `201×4, 409×3, 404, 403×3, 410×3, 401`; CU-09 `200×4, 403, 403, 404, 401`; CU-10 `200×4, 403, 403, 404, 401`; CU-11 `200, 200, 404, 403, 401`; CU-12 `200×3, 409, 409, 404, 403, 403, 503, 401`.
2. **Ajuste de ADR-012 (aprobado por el usuario el 2026-11-20):** el Coordinador sube el `.xlsx` y openpyxl 3.1.5 (MIT) lo lee detrás del puerto `LectorExcel`. El camino del libro ya leído se conserva y da el mismo resultado (ESC-XL). Después del ajuste, la regresión de CU-01 a CU-12 y de CU-14 da los mismos códigos.

## Anexo: script de ejecución

```python
"""Ejecuta los escenarios de specs/013 contra la composicion de src/main.py."""
import sys
from datetime import datetime, timedelta
sys.path.insert(0, sys.argv[1])
from main import construir

VALIDO = {
    "Empresas": [{"id": "EMP-H1", "razon_social": "Histórica S.A."}],
    "Plazas": [{"id": "PL-H1", "id_empresa": "EMP-H1", "cargo": "Analista", "cupos": "3", "periodo": "2026-2"}],
    "Tutores": [{"id": "T-H1", "correo": "th1@universidad.edu.co"}],
    "Estudiantes": [{"id": "E-H1", "correo": "eh1@universidad.edu.co"}],
    "Practicas": [{"id": "PR-H1", "id_estudiante": "E-H1", "id_empresa": "EMP-H1", "id_tutor": "T-H1"}],
}
CON_ERRORES = {
    "Empresas": VALIDO["Empresas"] + [{"id": "EMP-ACME", "razon_social": "Acme"}, {"id": "EMP-H2", "razon_social": ""}],
    "Plazas": VALIDO["Plazas"] + [
        {"id": "PL-H2", "id_empresa": "EMP-99", "cargo": "X", "cupos": "1", "periodo": "2026-2"},
        {"id": "PL-H3", "id_empresa": "EMP-H1", "cargo": "X", "cupos": "tres", "periodo": "2026-2"},
        {"id": "PL-H4", "id_empresa": "EMP-H1", "cargo": "X", "cupos": "0", "periodo": "2026-2"},
    ],
    "Tutores": VALIDO["Tutores"] + [{"id": "T-H2", "correo": "sin-arroba"}],
    "Estudiantes": VALIDO["Estudiantes"],
    "Practicas": VALIDO["Practicas"] + [
        {"id": "PR-H2", "id_estudiante": "E-99", "id_empresa": "EMP-H1", "id_tutor": "T-H1"},
        {"id": "PR-H3", "id_estudiante": "E-H1", "id_empresa": "EMP-H1", "id_tutor": "T-99"},
    ],
}


def app():
    a = construir()
    return a, a["controlador"], a["repositorio"], a["bitacora"]


def importar(c, hojas, token="tok-C-01"):
    return c.importar_historico(token, {"hojas": hojas})


def cargado(r):
    p = r.obtener_practica("PR-H1")
    return {"empresa": r.obtener_empresa("EMP-H1"), "plaza": r.obtener_plaza("PL-H1"), "tutor": r.obtener_tutor("T-H1"),
            "estudiante": r.obtener_estudiante("E-H1"), "practica": p and (str(p.estado), p.id_tutor, p.version_regla)}


print("== ESC-B")
a, c, r, b = app()
print(" HTTP", *importar(c, VALIDO))
print(" cargado:", cargado(r))
print(" bitacora:", [(x["usuario"], x["recurso"], x["accion"]) for x in b.listar()])

print("== ESC-RE")
a, c, r, b = app()
estado, cuerpo = importar(c, CON_ERRORES)
print(" HTTP", estado, "cargadas:", cuerpo["cargadas"])
for f in cuerpo["rechazadas"]:
    print("  rechazada:", f)
print(" no cargadas:", [r.obtener_empresa("EMP-H2"), r.obtener_plaza("PL-H2"), r.obtener_plaza("PL-H3"), r.obtener_plaza("PL-H4"),
                        r.obtener_tutor("T-H2"), r.obtener_practica("PR-H2"), r.obtener_practica("PR-H3")],
      "| EMP-ACME sigue:", r.obtener_empresa("EMP-ACME"))

print("== ESC-DO")
a, c, r, b = app()
importar(c, VALIDO)
estado, cuerpo = importar(c, VALIDO)
print(" HTTP", estado, "cargadas:", cuerpo["cargadas"])
for f in cuerpo["rechazadas"]:
    print("  rechazada:", f)

print("== ESC-HD")
a, c, r, b = app()
print(" HTTP", *importar(c, {"Notas": [{"x": "1"}]}))

print("== ESC-SR")
a, c, r, b = app()
print(" HTTP", *importar(c, VALIDO, token="tok-T-500"))
print(" cargado:", cargado(r))
print(" bitacora:", b.listar())

print("== ESC-TV")
a, c, r, b = app()
a["proveedor"].emitir("tok-C-vencido", "C-01", "CoordinadorPracticas", datetime.now() - timedelta(minutes=16))
print(" HTTP", *importar(c, VALIDO, token="tok-C-vencido"))
print(" cargado:", cargado(r))


# --- Ajuste ADR-012: el Coordinador sube el archivo .xlsx real ---
from io import BytesIO
from openpyxl import Workbook


def a_xlsx(hojas, numeros=True):
    """Arma un .xlsx real; los cupos que son numeros se escriben como numero, como en una hoja de Excel."""
    libro = Workbook()
    libro.remove(libro.active)
    for nombre, filas in hojas.items():
        hoja = libro.create_sheet(nombre)
        encabezado = list(filas[0].keys())
        hoja.append(encabezado)
        for fila in filas:
            hoja.append([float(v) if numeros and k == "cupos" and v.lstrip("-").isdigit() else v for k, v in fila.items()])
        hoja.append([None] * len(encabezado))  # fila vacia al final: se ignora
    salida = BytesIO()
    libro.save(salida)
    return salida.getvalue()


print("== ESC-XL")
a, c, r, b = app()
archivo = a_xlsx(CON_ERRORES)
open(sys.argv[2] if len(sys.argv) > 2 else "historico_cu13.xlsx", "wb").write(archivo)
estado, cuerpo = c.importar_historico_excel("tok-C-01", archivo)
print(" bytes del .xlsx:", len(archivo), "| empieza con:", archivo[:2])
print(" HTTP", estado, "cargadas:", cuerpo["cargadas"])
for f in cuerpo["rechazadas"]:
    print("  rechazada:", f)
print(" igual que con el libro ya leido:", cuerpo == importar(app()[1], CON_ERRORES)[1])
print(" PL-H1 cupos (3.0 en Excel):", r.obtener_plaza("PL-H1").cupos)

print("== ESC-AN")
a, c, r, b = app()
print(" HTTP", *c.importar_historico_excel("tok-C-01", b"esto no es un excel"))
print(" cargado:", cargado(r))

print("== ESC-XS")
a, c, r, b = app()
print(" HTTP", *c.importar_historico_excel("tok-T-500", a_xlsx(VALIDO)))
print(" cargado:", cargado(r), "| bitacora:", [(x["usuario"], x["recurso"], x["accion"]) for x in b.listar()])
```
