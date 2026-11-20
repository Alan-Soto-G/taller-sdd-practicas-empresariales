# Validación: 002 Publicar plazas de práctica

Fecha: 2026-11-20. Código validado: `src/` en el commit `ab5face` (002 T-11).

Método: cada escenario se ejecutó contra la composición real de `src/main.py` (`construir()`), con una aplicación nueva por escenario y los datos de los Antecedentes de [spec.md](spec.md): la Empresa "EMP-ACME" y el Coordinador "C-01" con el token `tok-C-01`. El script de ejecución está en el Anexo, porque en esta etapa no hay carpeta de pruebas automatizadas (`AGENTS.md`). Se ejecuta con `python -B validar_cu02.py <ruta>/src`.

## Validación funcional

| Escenario | Resultado | Evidencia |
|-----------|-----------|-----------|
| ESC-B Flujo básico | Cumple | `HTTP 201 {'id': 'PL-123ddb95', 'id_empresa': 'EMP-ACME', 'cargo': 'Practicante de desarrollo', 'cupos': 2, 'periodo': '2026-2', 'mensaje': 'plaza publicada'}`. Plaza nueva `('PL-123ddb95', 'EMP-ACME', 'Practicante de desarrollo', 2, '2026-2')`. Bitácora nueva: `[]`. Código: `src/aplicacion/postulaciones/publicar_plaza.py:61-75`, `src/infraestructura/controlador_rest.py:65-93` |
| ESC-PO Postulación a la plaza recién publicada (CU-01) | Cumple | Publicación `HTTP 201 id=PL-a07a43d0`. Luego `postular('tok-E-1001', PL-a07a43d0)` da `(201, {'id': 'PO-ba94d7f7', 'id_plaza': 'PL-a07a43d0', 'estado': 'enviada', …})`. Postulaciones: `[('E-1001', 'PL-a07a43d0', 'enviada')]`. Código: `src/infraestructura/repositorio_practicas_memoria.py:66-68` (`guardar_plaza` escribe en el mismo almacén que lee `obtener_plaza`) |
| ESC-DU Otra plaza igual, misma empresa y periodo | Cumple | `HTTP 201 {'id': 'PL-659aca42', …, 'cupos': 1, 'periodo': '2026-2', …}`. Plazas de EMP-ACME en 2026-2: `['PL-01', 'PL-659aca42']`, con ids distintos. Código: `publicar_plaza.py:61-67` (id `PL-<8 hex>`) |
| ESC-EN Empresa inexistente (EMP-99) | Cumple | `HTTP 404 {'codigo': 'empresa_no_encontrada', 'mensaje': 'empresa no encontrada', 'correlacion': …}`. Plazas nuevas: `[]`. Código: `publicar_plaza.py:50-51`, `controlador_rest.py:22` |
| ESC-DI cupos 0 | Cumple | `HTTP 400 {'codigo': 'plaza_no_valida', 'mensaje': 'plaza no válida', …, 'motivo': 'los cupos deben ser mayores que cero'}`. Plazas nuevas: `[]`. Código: `src/dominio/plaza.py:26-27`, `publicar_plaza.py:53-59` |
| ESC-DI cupos -1 | Cumple | `HTTP 400 … 'motivo': 'los cupos deben ser mayores que cero'`. Plazas nuevas: `[]` |
| ESC-DI cargo vacío | Cumple | `HTTP 400 … 'motivo': 'el cargo es obligatorio'`. Plazas nuevas: `[]`. Código: `plaza.py:24-25` |
| ESC-DI periodo "2026-3" | Cumple | `HTTP 400 … 'motivo': 'el periodo debe tener el formato AAAA-1 o AAAA-2'`. Plazas nuevas: `[]`. Código: `plaza.py:6,28-29` |
| ESC-DI periodo "2026" | Cumple | `HTTP 400 … 'motivo': 'el periodo debe tener el formato AAAA-1 o AAAA-2'`. Plazas nuevas: `[]` |
| ESC-SR Usuario sin rol CoordinadorPracticas (E-1001) | Cumple | `HTTP 403 {'codigo': 'acceso_denegado', 'mensaje': 'acceso denegado', …}`. Plazas nuevas: `[]`. Bitácora: `{'usuario': 'E-1001', 'rol': 'Estudiante', 'recurso': 'empresa:EMP-ACME', 'accion': 'publicar plaza', 'hora': 2026-11-20 03:33:26}`. Código: `publicar_plaza.py:40-48` |
| ESC-TV Token emitido hace 16 minutos | Cumple | `HTTP 401 {'codigo': 'no_autenticado', 'mensaje': 'no autenticado', …}`. Plazas nuevas: `[]`. Bitácora nueva: `[]`. Código: `controlador_rest.py:72` (valida el token antes de llamar al caso de uso), `src/infraestructura/proveedor_identidad_simulado.py:9,30` |

En ningún escenario de rechazo por validación o por empresa inexistente se escribe en la bitácora, como decidió la spec. Todas las respuestas de error llevan `codigo`, `mensaje` y `correlacion` (`controlador_rest.py:95-108`), y `motivo` cuando es `PlazaNoValida` (`controlador_rest.py:106`).

## Validación arquitectónica

- **Regla de dependencia: cumple.** `src/dominio/` solo importa `re`, `dataclasses`, `enum`, `datetime` y `dominio.estado_postulacion`. Ningún archivo de `src/aplicacion/` importa `infraestructura`; la palabra solo aparece en los docstrings de los puertos ("Lo implementa infraestructura").
- **Cada ADR del plan se ve en el código:**
  - ADR-002: `PublicarPlaza` está en el Módulo Postulaciones (`src/aplicacion/postulaciones/`), junto a CU-01. El puerto sigue siendo `Protocol` (`src/aplicacion/puertos/repositorio_practicas.py:9`), con `obtener_empresa` y `guardar_plaza` (`:30`, `:34`). `src/main.py` es la única composición (`main.py:22-25`).
  - ADR-003: el adaptador en memoria implementa los métodos nuevos (`repositorio_practicas_memoria.py:62-72`).
  - ADR-004: la autorización por rol está en el caso de uso (`publicar_plaza.py:17,40`), no en el controlador. Se reutiliza el token de 15 minutos de CU-01.
  - ADR-006: se audita el acceso rechazado con usuario, rol, recurso, acción y hora (`publicar_plaza.py:41-47`). Publicar la Plaza no se audita (decisión de la spec).
  - ADR-007: errores `EmpresaNoEncontrada` y `PlazaNoValida` en `src/aplicacion/errores/`. La traducción a 404 y 400 está en `controlador_rest.py:22-23`.
- **Convenciones de AGENTS.md: cumplen.** Python 3.12 (`str | None`, `re.fullmatch`). Una clase por archivo en todo `src/` (`main.py` solo tiene funciones). Cero `__init__.py` y ningún archivo con BOM. DTO `SolicitudPublicacionPlaza` en la entrada y `PlazaPublicada` en la salida. Nombres del glosario (`Empresa`, `Plaza`, `CoordinadorPracticas`, `RepositorioPracticas`, `Bitacora`). Solo librería estándar. Sin base de datos ni servicios reales.

### Observaciones (no se corrigen en esta fase)

1. **CU-01 no se rompió.** El script del Anexo de [001/validacion.md](../001-postularse-plaza-practica/validacion.md) se volvió a ejecutar contra este `src/`. Los 11 escenarios dan el mismo resultado: ESC-B 201, ESC-SC 409, ESC-AP 409, ESC-OP 201, ESC-MP 409 (×2), ESC-VP 201, ESC-NE 404, ESC-SR 403 con su registro en la bitácora, ESC-TV 401 y ESC-CC `[201, 201]`.
2. **Tipo de `cupos` en el controlador:** `controlador_rest.py:77` pasa `cuerpo.get("cupos", 0)` sin convertirlo. Si un cliente enviara `cupos` como texto, `Plaza.motivo_invalidez` lanzaría `TypeError` (que no es un error de aplicación) en lugar de responder 400. Ningún escenario de la spec lo cubre. Se resolverá cuando un ADR apruebe el servidor HTTP y su validación de entrada.
3. **Estado intermedio entre commits:** entre `002 T-10` y `002 T-11`, `main.py` todavía construía `ControladorRest` con dos argumentos. Es consecuencia del orden de adentro hacia afuera de `tasks.md`, y `002 T-11` lo resolvió.
4. **Anomalías de proceso:** en T-06, la primera ejecución de Codex terminó sin escribir el archivo. La segunda lo escribió sin el salto de línea final, que se agregó en la auditoría. Ningún archivo de `src/` tiene BOM.

## Anexo: script de ejecución

```python
"""Ejecuta los escenarios de specs/002 contra la composicion de src/main.py."""
import sys
sys.path.insert(0, sys.argv[1])
from main import construir
from dominio.plaza import Plaza


def app():
    a = construir()
    return a, a["controlador"], a["repositorio"], a["bitacora"]


def plazas(repo):
    return [(p.id, p.id_empresa, p.cargo, p.cupos, p.periodo) for p in repo.listar_plazas()]


def publicar(c, token, id_empresa="EMP-ACME", cargo="Practicante de desarrollo", cupos=2, periodo="2026-2"):
    return c.publicar_plaza(token, {"id_empresa": id_empresa, "cargo": cargo, "cupos": cupos, "periodo": periodo})


def esc(nombre, repo, bit, antes_p, antes_b, http):
    print(f"== {nombre}")
    print(f"  HTTP {http[0]} {http[1]}")
    print(f"  plazas nuevas: {[p for p in plazas(repo) if p not in antes_p]}")
    print(f"  bitacora nueva: {bit.listar()[antes_b:]}")


# ESC-B
a, c, r, b = app(); p0, b0 = plazas(r), len(b.listar())
esc("ESC-B", r, b, p0, b0, publicar(c, "tok-C-01"))

# ESC-PO: la plaza recien publicada admite la postulacion de CU-01
a, c, r, b = app()
estado, cuerpo = publicar(c, "tok-C-01")
print(f"== ESC-PO\n  publicacion: HTTP {estado} id={cuerpo['id']}")
print(f"  postulacion: {c.postular('tok-E-1001', {'id_plaza': cuerpo['id']})}")
print(f"  postulaciones: {[(p.id_estudiante, p.id_plaza, str(p.estado)) for p in r.listar_postulaciones()]}")

# ESC-DU: otra plaza igual de la misma empresa en el mismo periodo
a, c, r, b = app()
p0, b0 = plazas(r), len(b.listar())
esc("ESC-DU", r, b, p0, b0, publicar(c, "tok-C-01", cupos=1))
print(f"  plazas de EMP-ACME en 2026-2: {[p[0] for p in plazas(r) if p[1] == 'EMP-ACME' and p[4] == '2026-2']}")

# ESC-EN
a, c, r, b = app(); p0, b0 = plazas(r), len(b.listar())
esc("ESC-EN", r, b, p0, b0, publicar(c, "tok-C-01", id_empresa="EMP-99", cargo="Practicante", cupos=1))

# ESC-DI (esquema)
for cargo, cupos, periodo in [("Practicante", 0, "2026-2"), ("Practicante", -1, "2026-2"),
                              ("", 2, "2026-2"), ("Practicante", 2, "2026-3"), ("Practicante", 2, "2026")]:
    a, c, r, b = app(); p0, b0 = plazas(r), len(b.listar())
    esc(f"ESC-DI cargo={cargo!r} cupos={cupos} periodo={periodo!r}", r, b, p0, b0,
        publicar(c, "tok-C-01", cargo=cargo, cupos=cupos, periodo=periodo))

# ESC-SR
a, c, r, b = app(); p0, b0 = plazas(r), len(b.listar())
esc("ESC-SR", r, b, p0, b0, publicar(c, "tok-E-1001", cargo="Practicante", cupos=1))

# ESC-TV
a, c, r, b = app(); p0, b0 = plazas(r), len(b.listar())
esc("ESC-TV", r, b, p0, b0, publicar(c, "tok-vencido", cargo="Practicante", cupos=1))
```
