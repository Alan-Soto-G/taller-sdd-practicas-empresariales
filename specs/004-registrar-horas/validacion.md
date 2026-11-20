# Validación: 004 Registrar horas de práctica

Fecha: 2026-11-20. Código validado: `src/` en el commit `3151420` (004 T-11).

Método: cada escenario se ejecutó contra la composición real de `src/main.py` (`construir()`), con una aplicación nueva por escenario y los datos de los Antecedentes de [spec.md](spec.md): Estudiante "E-1004" (`tok-E-1004`) con la Practica "PR-04" "en curso", Estudiante "E-1001" (`tok-E-1001`) con la Practica "PR-01" "sin tutor" y el Tutor "T-300" (`tok-T-300`). Para EAC-01 se agregan 300 estudiantes, prácticas "en curso" y tokens, y las peticiones se lanzan a la vez con 300 hilos. El script está en el Anexo. Se ejecuta con `python -B validar_cu04.py <ruta>/src`.

## Validación funcional

| Escenario | Resultado | Evidencia |
|-----------|-----------|-----------|
| ESC-B Flujo básico | Cumple | Registros antes `[]`. `HTTP 201 {'id': 'RH-2237609e', 'id_practica': 'PR-04', 'semana': '2026-W47', 'horas': 20, 'estado': 'reportado', 'fecha': '2026-11-20', 'mensaje': 'horas reportadas, pendientes de aprobación del tutor'}`. Registros `[('PR-04', '2026-W47', 20, 'reportado')]`. Bitácora: `{'usuario': 'E-1004', 'rol': 'Estudiante', 'recurso': 'registro_horas:RH-2237609e', 'accion': 'crear con estado reportado', 'hora': …}`. Código: `src/aplicacion/horas/registrar_horas.py:68-94` |
| ESC-OS Otra semana | Cumple | `HTTP 201` semana "2026-W48", 18 horas. Registros `[('PR-04', '2026-W47', 20, 'reportado'), ('PR-04', '2026-W48', 18, 'reportado')]` |
| ESC-SR2 Semana con registro | Cumple | `HTTP 422 {'codigo': 'registro_no_valido', 'mensaje': 'registro no válido', …, 'motivo': 'la semana ya tiene un registro'}`. Registros `[('PR-04', '2026-W47', 20, 'reportado')]` (sigue 1). Código: `registrar_horas.py:62-66` |
| ESC-DI horas 0 | Cumple | `HTTP 422 … 'motivo': 'las horas deben estar entre 1 y 168'`. Registros `[]`, bitácora `[]`. Código: `src/dominio/registro_horas.py:50-51` |
| ESC-DI horas -5 | Cumple | `HTTP 422 … 'motivo': 'las horas deben estar entre 1 y 168'`. Registros `[]` |
| ESC-DI horas 169 | Cumple | `HTTP 422 … 'motivo': 'las horas deben estar entre 1 y 168'`. Registros `[]` |
| ESC-DI sin actividades | Cumple | `HTTP 422 … 'motivo': 'las actividades son obligatorias'`. Registros `[]` |
| ESC-DI semana "2026-47" | Cumple | `HTTP 422 … 'motivo': 'la semana debe tener el formato AAAA-Wss (semana 01 a 53)'`. Registros `[]`. Código: `registro_horas.py:9,48-49` |
| ESC-DI semana "2026-W54" | Cumple | `HTTP 422 … 'motivo': 'la semana debe tener el formato AAAA-Wss (semana 01 a 53)'`. Registros `[]` |
| ESC-NC Práctica no en curso (PR-01) | Cumple | `HTTP 422 … 'motivo': 'la práctica no está en curso'`. Registros `[]`. Código: `registrar_horas.py:51-52` |
| ESC-PN Práctica inexistente | Cumple | `HTTP 404 {'codigo': 'practica_no_encontrada', 'mensaje': 'práctica no encontrada', …}`. Registros `[]`. Código: `registrar_horas.py:44-46`, `src/infraestructura/controlador_rest.py:31` |
| ESC-AJ EAC-04 práctica ajena | Cumple | `E-1001` sobre `PR-04`: `HTTP 403 {'codigo': 'acceso_denegado', …}`. Registros `[]`. Bitácora: `{'usuario': 'E-1001', 'rol': 'Estudiante', 'recurso': 'practica:PR-04', 'accion': 'registrar horas', 'hora': …}`, es decir usuario, recurso y hora (medida de EAC-04). Código: `registrar_horas.py:48-49`, `:96-110` |
| ESC-SR Sin rol Estudiante | Cumple | `T-300`: `HTTP 403 {'codigo': 'acceso_denegado', …}`. Registros `[]`. Bitácora: `{'usuario': 'T-300', 'rol': 'Tutor', 'recurso': 'practica:PR-04', 'accion': 'registrar horas', 'hora': …}`. Código: `registrar_horas.py:41-42` |
| ESC-TV Token de hace 16 minutos | Cumple | `HTTP 401 {'codigo': 'no_autenticado', …}`. Registros `[]`, bitácora `[]` |
| ESC-CA EAC-01, 300 simultáneos | Cumple | Códigos `{201: 300}`. p95 0,03 ms, máximo 0,04 ms: el 100% de las confirmaciones tarda menos de 2 s (medida: 95%). 300 registros en 300 prácticas distintas, todos `reportado`: 0 perdidos y 0 duplicados |
| ESC-DU EAC-01, mismo registro dos veces a la vez | Cumple | Respuestas `[(201, None), (422, 'la semana ya tiene un registro')]`. Registros de PR-04 `[('PR-04', '2026-W47', 20, 'reportado')]`. Código: `src/infraestructura/repositorio_practicas_memoria.py:145-151` (comprueba y agrega dentro del `Lock`), `registrar_horas.py:76-78` |

## Validación arquitectónica

- **Regla de dependencia: cumple.** `src/dominio/` solo importa `dataclasses`, `datetime`, `enum`, `re` y módulos de `dominio`. Ningún archivo de `src/aplicacion/` importa `infraestructura`.
- **Cada ADR del plan se ve en el código:**
  - ADR-001: `RegistrarHoras` solo valida y guarda; no hay trabajo pesado en la petición (EAC-01).
  - ADR-002: caso de uso en el Módulo Horas (`src/aplicacion/horas/`); puerto `RepositorioPracticas` como `Protocol`; `main.py:41` lo compone.
  - ADR-003: el adaptador en memoria implementa `existe_registro_horas` y `guardar_registro_horas`; la operación atómica cumple el papel de la restricción única de PostgreSQL.
  - ADR-004: autorización por rol (`registrar_horas.py:41`) y por titularidad (`:48`) en el caso de uso, no en el controlador.
  - ADR-006: se audita la creación del registro (`registrar_horas.py:80-86`) y cada acceso rechazado (`:103-109`), con usuario, rol, recurso, acción y hora.
  - ADR-007: `PracticaNoEncontrada` (404) y `RegistroNoValido` con motivo (422, como en la secuencia) en `controlador_rest.py:31,34,183`.
- **Convenciones de AGENTS.md: cumplen.** Una clase por archivo, cero `__init__.py`, ningún archivo con BOM. DTO `SolicitudRegistroHoras` y `HorasReportadas`. Nombres del glosario (`RegistroHoras`, `EstadoRegistroHoras`, `Practica`). Solo librería estándar (`threading` en el adaptador).

### Observaciones (no se corrigen en esta fase)

1. **CU-01 a CU-03 no se rompieron.** Los scripts de los Anexos de 001, 002 y 003 dan los mismos códigos: CU-01 `201, 409, 409, 201, 409, 409, 201, 404, 403, 401, [201, 201]`; CU-02 `201, 201, 201, 404, 400×5, 403, 401`; CU-03 los mismos resultados por práctica, más `404, 403, 401`.
2. **Alcance de la medida de EAC-01:** los tiempos son de la composición en memoria, sin red ni PostgreSQL. La medida real se toma con la prueba de carga antes del primer cierre (R-02), fuera de esta spec.
3. **Tipo de `horas` en el controlador:** igual que `cupos` en 002, `controlador_rest.py` pasa `cuerpo.get("horas", 0)` sin convertirlo; un texto en lugar de un número lanzaría `TypeError`. Ningún escenario lo cubre.
4. **Proceso:** en T-03, Codex escribió el archivo pero no terminó y hubo que detener su proceso. Por el protocolo de fallback, las micro-tareas siguientes pasaron a agy.

## Anexo: script de ejecución

```python
"""Ejecuta los escenarios de specs/004 contra la composicion de src/main.py."""
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
sys.path.insert(0, sys.argv[1])
from main import construir
from dominio.estado_practica import EstadoPractica
from dominio.estudiante import Estudiante
from dominio.practica import Practica


def app():
    a = construir()
    return a, a["controlador"], a["repositorio"], a["bitacora"]


def regs(repo, id_practica=None):
    return [(r.id_practica, r.semana, r.horas, str(r.estado)) for r in repo.listar_registros_horas()
            if id_practica is None or r.id_practica == id_practica]


def registrar(c, token, id_practica, semana="2026-W47", horas=20, actividades="Desarrollo del módulo de reportes"):
    return c.registrar_horas(token, id_practica, {"semana": semana, "horas": horas, "actividades": actividades})


print("== ESC-B")
a, c, r, b = app()
print(" registros antes:", regs(r, "PR-04"))
print(" HTTP", *registrar(c, "tok-E-1004", "PR-04"))
print(" registros:", regs(r, "PR-04"))
print(" bitacora:", b.listar())

print("== ESC-OS")
a, c, r, b = app()
registrar(c, "tok-E-1004", "PR-04")
print(" HTTP", *registrar(c, "tok-E-1004", "PR-04", "2026-W48", 18, "Pruebas"))
print(" registros:", regs(r, "PR-04"))

print("== ESC-SR2")
a, c, r, b = app()
registrar(c, "tok-E-1004", "PR-04")
print(" HTTP", *registrar(c, "tok-E-1004", "PR-04", "2026-W47", 10, "Otra vez"))
print(" registros:", regs(r, "PR-04"))

for horas, semana, act in [(0, "2026-W47", "Desarrollo"), (-5, "2026-W47", "Desarrollo"), (169, "2026-W47", "Desarrollo"),
                           (20, "2026-W47", ""), (20, "2026-47", "Desarrollo"), (20, "2026-W54", "Desarrollo")]:
    print(f"== ESC-DI horas={horas} semana={semana!r} actividades={act!r}")
    a, c, r, b = app()
    print(" HTTP", *registrar(c, "tok-E-1004", "PR-04", semana, horas, act))
    print(" registros:", regs(r), "bitacora:", b.listar())

print("== ESC-NC")
a, c, r, b = app()
print(" HTTP", *registrar(c, "tok-E-1001", "PR-01", actividades="Inducción"))
print(" registros:", regs(r))

print("== ESC-PN")
a, c, r, b = app()
print(" HTTP", *registrar(c, "tok-E-1004", "PR-99"))
print(" registros:", regs(r))

print("== ESC-AJ")
a, c, r, b = app()
print(" HTTP", *registrar(c, "tok-E-1001", "PR-04"))
print(" registros:", regs(r))
print(" bitacora:", b.listar())

print("== ESC-SR")
a, c, r, b = app()
print(" HTTP", *registrar(c, "tok-T-300", "PR-04"))
print(" registros:", regs(r))
print(" bitacora:", b.listar())

print("== ESC-TV")
a, c, r, b = app()
a["proveedor"].emitir("tok-E-1004-vencido", "E-1004", "Estudiante", datetime.now() - timedelta(minutes=16))
print(" HTTP", *registrar(c, "tok-E-1004-vencido", "PR-04"))
print(" registros:", regs(r), "bitacora:", b.listar())

print("== ESC-CA")
a, c, r, b = app()
ahora = datetime.now()
for k in range(300):
    r.agregar_estudiante(Estudiante(f"E-5{k:03d}", f"e5{k:03d}@universidad.edu.co"))
    r.agregar_practica(Practica(f"PC-{k:03d}", f"E-5{k:03d}", "EMP-ACME", "v1", EstadoPractica.EN_CURSO, "T-300"))
    a["proveedor"].emitir(f"tok-E-5{k:03d}", f"E-5{k:03d}", "Estudiante", ahora)


def una(k):
    t0 = time.perf_counter()
    estado, _ = registrar(c, f"tok-E-5{k:03d}", f"PC-{k:03d}")
    return estado, time.perf_counter() - t0


with ThreadPoolExecutor(max_workers=300) as ex:
    resultados = list(ex.map(una, range(300)))
tiempos = sorted(t for _, t in resultados)
p95 = tiempos[int(0.95 * len(tiempos)) - 1]
bajo_2s = sum(1 for t in tiempos if t < 2) / len(tiempos)
registros = [x for x in regs(r) if x[0].startswith("PC-")]
print(" codigos:", {e: sum(1 for x, _ in resultados if x == e) for e, _ in resultados})
print(f" p95={p95 * 1000:.2f} ms, maximo={tiempos[-1] * 1000:.2f} ms, confirmaciones < 2 s: {bajo_2s:.0%}")
print(" registros:", len(registros), "practicas distintas:", len({x[0] for x in registros}),
      "estados:", {x[3] for x in registros})

print("== ESC-DU")
a, c, r, b = app()
with ThreadPoolExecutor(max_workers=2) as ex:
    dos = list(ex.map(lambda _: registrar(c, "tok-E-1004", "PR-04"), range(2)))
print(" respuestas:", sorted((e, x.get("motivo")) for e, x in dos))
print(" registros:", regs(r, "PR-04"))
```
