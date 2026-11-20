# Validación: 001 Postularse a una plaza de práctica

Fecha: 2026-11-20. Código validado: `src/` en el commit `a4dee0f` (T-21).

Método: cada escenario se ejecutó contra la composición real de `src/main.py` (`construir()`), con una aplicación nueva por escenario y los datos de los Antecedentes de [spec.md](spec.md). El script de ejecución está en el Anexo, porque en esta etapa no hay carpeta de pruebas automatizadas (`AGENTS.md`). Se ejecuta con `python -B validar_cu01.py <ruta>/src`.

## Validación funcional

| Escenario | Resultado | Evidencia |
|-----------|-----------|-----------|
| ESC-B Flujo básico | Cumple | `HTTP 201 {'id': 'PO-251d578f', 'id_plaza': 'PL-01', 'estado': 'enviada', 'fecha': '2026-11-20', 'mensaje': 'postulación enviada'}`. Postulación nueva `('E-1001', 'PL-01', 'enviada')`. Bitácora: `{'usuario': 'E-1001', 'rol': 'Estudiante', 'recurso': 'postulacion:PO-251d578f', 'accion': 'crear con estado enviada', 'hora': 2026-11-20 01:41:18}`. Código: `src/aplicacion/postulaciones/postularse_plaza.py:67-87` |
| ESC-SC Plaza sin cupos (2 de 2 aceptadas) | Cumple | `HTTP 409 {'codigo': 'postulacion_no_permitida', 'mensaje': 'postulación no permitida', 'motivo': 'la plaza no tiene cupos disponibles'}`. Postulaciones nuevas: `[]`. Bitácora nueva: `[]`. Código: `postularse_plaza.py:62-65`, `src/dominio/plaza.py` (`tiene_cupo`) |
| ESC-AP Postulación aceptada en el periodo | Cumple | `HTTP 409 … 'motivo': 'ya tienes una postulación aceptada en el periodo'`. Postulaciones nuevas: `[]`. Código: `postularse_plaza.py:55-60` |
| ESC-OP Aceptada en otro periodo (2026-1) | Cumple | `HTTP 201 … 'estado': 'enviada'`. Postulación nueva `('E-1001', 'PL-01', 'enviada')` |
| ESC-MP Misma plaza (enviada) | Cumple | `HTTP 409 … 'motivo': 'ya te postulaste a esta plaza'`. Postulaciones de E-1001 a PL-01: `1`. Código: `postularse_plaza.py:52-53` |
| ESC-MP Misma plaza (rechazada) | Cumple | `HTTP 409 … 'motivo': 'ya te postulaste a esta plaza'`. Postulaciones de E-1001 a PL-01: `1` |
| ESC-VP Enviadas a otras plazas | Cumple | `HTTP 201 … 'estado': 'enviada'`. Enviadas de E-1001 en 2026-2: `2` |
| ESC-NE Plaza inexistente (PL-99) | Cumple | `HTTP 404 {'codigo': 'plaza_no_encontrada', 'mensaje': 'plaza no encontrada', …}`. Postulaciones nuevas: `[]`. Código: `postularse_plaza.py:48-50` |
| ESC-SR Usuario sin rol Estudiante (T-200) | Cumple | `HTTP 403 {'codigo': 'acceso_denegado', 'mensaje': 'acceso denegado', …}`. Postulaciones nuevas: `[]`. Bitácora: `{'usuario': 'T-200', 'rol': 'Tutor', 'recurso': 'plaza:PL-01', 'accion': 'postularse', 'hora': 2026-11-20 01:41:18}`. Código: `postularse_plaza.py:38-46` |
| ESC-TV Token emitido hace 16 minutos | Cumple | `HTTP 401 {'codigo': 'no_autenticado', 'mensaje': 'no autenticado', …}`. Postulaciones nuevas: `[]`. Código: `src/infraestructura/proveedor_identidad_simulado.py:9,30` |
| ESC-CC Dos estudiantes, un cupo libre | Cumple | Dos hilos simultáneos: `HTTP [201, 201]`. Enviadas a PL-01: `2`. Aceptadas en PL-01: `1` |

Todas las respuestas de error llevan `codigo`, `mensaje` y `correlacion` (`src/infraestructura/controlador_rest.py:62-70`).

## Validación arquitectónica

- **Regla de dependencia: cumple.** `src/dominio/` solo importa `enum`, `dataclasses`, `datetime` y `dominio.estado_postulacion`. Ningún archivo de `src/aplicacion/` importa `infraestructura`.
- **Cada ADR del plan se ve en el código:**
  - ADR-002: capas `src/dominio/`, `src/aplicacion/` y `src/infraestructura/`. Los puertos son `Protocol` en `src/aplicacion/puertos/` (`repositorio_practicas.py:8`, `bitacora.py:7`, `proveedor_identidad.py:8`). `src/main.py` es la única composición.
  - ADR-003: `RepositorioPracticas` lo implementa el adaptador en memoria `src/infraestructura/repositorio_practicas_memoria.py`.
  - ADR-004: token de 15 minutos (`proveedor_identidad_simulado.py:9`, `VIDA_TOKEN`). La autorización por rol está en el caso de uso (`postularse_plaza.py:38`), no en el controlador.
  - ADR-006: se audita la creación (`postularse_plaza.py:75`) y el acceso rechazado (`postularse_plaza.py:39`), con usuario, rol, recurso, acción y hora.
  - ADR-007: catálogo en `src/aplicacion/errores/`. La traducción a 401, 403, 404 y 409 está en `controlador_rest.py:14-19`.
- **Convenciones de AGENTS.md: cumplen.** Python 3.12 (`StrEnum`, `X | None`). Una clase por archivo (20 archivos con 1 clase; `main.py` solo tiene funciones). Cero `__init__.py`. DTO `SolicitudPostulacion` en la entrada y `PostulacionEnviada` en la salida. Nombres del glosario (`Plaza`, `Postulacion`, `RepositorioPracticas`, `Bitacora`, `ProveedorIdentidad`). Solo librería estándar. Sin base de datos ni servicios reales.

### Observaciones (no se corrigen en esta fase)

1. **ADR-006, "misma transacción":** con los adaptadores en memoria, la postulación se guarda y la auditoría se escribe una tras otra (`postularse_plaza.py:74-81`), sin atomicidad real. Si `Bitacora.registrar` fallara, la postulación quedaría sin registro. El plan lo acepta para esta etapa. El adaptador PostgreSQL debe garantizar la transacción única.
2. **ESC-CC:** `RepositorioPracticasMemoria` no usa bloqueos. El escenario se cumple porque `list.append` es atómico en CPython y porque el cupo no se consume al enviar. No es evidencia de concurrencia segura para la futura persistencia real.
3. **Anomalía de proceso:** el primer obrero de T-01 (Codex) escribió el archivo con BOM UTF-8. Se corrigió en la revisión de T-01. Ningún archivo de `src/` tiene BOM hoy.

## Anexo: script de ejecución

```python
"""Ejecuta los escenarios de specs/001 contra la composicion de src/main.py."""
import sys
from datetime import date
from concurrent.futures import ThreadPoolExecutor
sys.path.insert(0, sys.argv[1])
from main import construir
from dominio.postulacion import Postulacion
from dominio.estado_postulacion import EstadoPostulacion as E

def pos(id, est, plaza, periodo, estado):
    return Postulacion(id, est, plaza, periodo, date(2026, 8, 1), estado)

def aceptadas(repo, n, plaza="PL-01"):
    for i in range(n):
        repo.guardar_postulacion(pos(f"PRE-{plaza}-{i}", f"E-90{i}", plaza, "2026-2", E.ACEPTADA))

def run(nombre, prep, token="tok-E-1001", plaza="PL-01"):
    app = construir(); repo, bit = app["repositorio"], app["bitacora"]
    prep(repo)
    antes_b = len(bit.listar()); antes = repo.listar_postulaciones()
    st, cuerpo = app["controlador"].postular(token, {"id_plaza": plaza})
    nuevas = [p for p in repo.listar_postulaciones() if p not in antes]
    print(f"== {nombre}\n  HTTP {st} {cuerpo}\n  postulaciones nuevas: {[(p.id_estudiante, p.id_plaza, str(p.estado)) for p in nuevas]}")
    print(f"  bitacora nueva: {bit.listar()[antes_b:]}")
    return app

run("ESC-B", lambda r: aceptadas(r, 1))
run("ESC-SC", lambda r: aceptadas(r, 2))
run("ESC-AP", lambda r: r.guardar_postulacion(pos("X1", "E-1001", "PL-02", "2026-2", E.ACEPTADA)))
run("ESC-OP", lambda r: r.guardar_postulacion(pos("X2", "E-1001", "PL-07", "2026-1", E.ACEPTADA)))
for est in (E.ENVIADA, E.RECHAZADA):
    app = run(f"ESC-MP ({est})", lambda r, est=est: r.guardar_postulacion(pos("X3", "E-1001", "PL-01", "2026-2", est)))
    print("  postulaciones de E-1001 a PL-01:", sum(1 for p in app["repositorio"].listar_postulaciones() if p.id_estudiante == "E-1001" and p.id_plaza == "PL-01"))
app = run("ESC-VP", lambda r: r.guardar_postulacion(pos("X4", "E-1001", "PL-02", "2026-2", E.ENVIADA)))
print("  enviadas de E-1001 en 2026-2:", sum(1 for p in app["repositorio"].listar_postulaciones() if p.id_estudiante == "E-1001" and p.periodo == "2026-2" and p.estado == E.ENVIADA))
run("ESC-NE", lambda r: None, plaza="PL-99")
run("ESC-SR", lambda r: None, token="tok-T-200")
run("ESC-TV", lambda r: None, token="tok-vencido")

print("== ESC-CC")
app = construir(); repo = app["repositorio"]; aceptadas(repo, 1)
with ThreadPoolExecutor(2) as ex:
    rs = list(ex.map(lambda t: app["controlador"].postular(t, {"id_plaza": "PL-01"}), ["tok-E-1001", "tok-E-1002"]))
print("  HTTP:", [r[0] for r in rs])
print("  enviadas a PL-01:", sum(1 for p in repo.listar_postulaciones() if p.id_plaza == "PL-01" and p.estado == E.ENVIADA))
print("  aceptadas en PL-01:", repo.contar_postulaciones_aceptadas("PL-01"))
```
