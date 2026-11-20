# Validación: 003 Asignar tutor a un estudiante

Fecha: 2026-11-20. Código validado: `src/` en el commit `172e2a6` (003 T-19).

Método: cada escenario se ejecutó contra la composición real de `src/main.py` (`construir()`), con una aplicación nueva por escenario y los datos de los Antecedentes de [spec.md](spec.md): ReglaPractica "v1" con carga máxima 2, Tutor "T-200", Estudiantes "E-1001" a "E-1003", Practicas "PR-01" y "PR-02" ("sin tutor") y "PR-03" ("en curso" con "T-300"), y el Coordinador "C-01" con el token `tok-C-01`. Las prácticas que ocupan la carga de "T-200" en algunos escenarios (`PX-*`, `PC-*`) se agregan con `agregar_practica`, y el cambio a la regla "v2" con `agregar_regla`. El script está en el Anexo (en esta etapa no hay carpeta de pruebas automatizadas, `AGENTS.md`). Se ejecuta con `python -B validar_cu03.py <ruta>/src`.

## Validación funcional

| Escenario | Resultado | Evidencia |
|-----------|-----------|-----------|
| ESC-B Flujo básico | Cumple | Carga antes 0. `HTTP 200 {'id_tutor': 'T-200', 'resultados': [{'id_practica': 'PR-01', 'resultado': 'asignada'}], 'mensaje': 'asignación procesada'}`. Práctica `('PR-01', 'T-200', 'en curso')`, carga 1. Bitácora: `{'usuario': 'C-01', 'rol': 'CoordinadorPracticas', 'recurso': 'practica:PR-01', 'accion': 'cambiar estado de sin tutor a en curso', 'hora': …}`. Correo a `['t200@universidad.edu.co', 'e1001@universidad.edu.co']`. Código: `src/aplicacion/asignacion/asignar_tutor.py:88-97`, `:100-118` |
| ESC-VA Varias prácticas a la vez | Cumple | `HTTP 200` con `PR-01: asignada` y `PR-02: asignada`. Prácticas `('PR-01', 'T-200', 'en curso')`, `('PR-02', 'T-200', 'en curso')`, carga 2. Bitácora con 2 registros de cambio de estado (`practica:PR-01`, `practica:PR-02`). Código: `asignar_tutor.py:64-98` (bucle en el orden recibido) |
| ESC-SC Tutor con la carga máxima | Cumple | Carga antes 2. `HTTP 200` con `PR-01: no asignada: tutor sin cupo`. Práctica `('PR-01', None, 'sin tutor')`, carga 2. Bitácora `[]`, correos `[]`. Código: `asignar_tutor.py:82-86`, `src/dominio/tutor.py:11-13` |
| ESC-CE Una práctica cerrada no cuenta | Cumple | Con 1 práctica "en curso" y 1 "cerrada", carga activa 1. `HTTP 200` con `PR-01: asignada`; práctica `('PR-01', 'T-200', 'en curso')`. Código: `src/dominio/practica.py:22-24`, `src/infraestructura/repositorio_practicas_memoria.py:117-123` |
| ESC-CP Cupo para una parte | Cumple | Carga antes 1. `HTTP 200` con `PR-01: asignada` y `PR-02: no asignada: tutor sin cupo`. Prácticas `('PR-01', 'T-200', 'en curso')`, `('PR-02', None, 'sin tutor')`, carga 2. Código: `asignar_tutor.py:96` (la carga crece dentro del bucle) |
| ESC-CO Falla el correo | Cumple | Con `notificador.disponible = False`: `HTTP 200` con `PR-01: asignada`; práctica `('PR-01', 'T-200', 'en curso')`. Enviados `[]`; pendientes de reenvío: `[{'destinatarios': ['t200@universidad.edu.co', 'e1001@universidad.edu.co'], 'asunto': 'Asignación de tutor', …}]`. Código: `src/infraestructura/notificador_simulado.py:14-25`, `asignar_tutor.py:117-118` |
| ESC-RV Cambio de la carga máxima a "v2" | Cumple | Carga antes 2; regla vigente `ReglaPractica(version='v2', horas_requeridas=160, carga_maxima_tutor=3, …)`. `HTTP 200` con `PR-01: asignada`; carga 3. Código: `asignar_tutor.py:60` (lee la regla vigente por el Módulo Configuración), `src/aplicacion/configuracion/consultar_regla_vigente.py:13-21` |
| ESC-YT La práctica ya tiene tutor | Cumple | `HTTP 200` con `PR-03: no asignada: la práctica ya tiene tutor`. Práctica `('PR-03', 'T-300', 'en curso')`; carga de T-200 0. Código: `asignar_tutor.py:74-80` |
| ESC-PN La práctica no existe | Cumple | `HTTP 200` con `PR-99: no asignada: práctica no encontrada`; carga de T-200 0. Código: `asignar_tutor.py:66-72` |
| ESC-TN El tutor no existe | Cumple | `HTTP 404 {'codigo': 'tutor_no_encontrado', 'mensaje': 'tutor no encontrado', 'correlacion': …}`. Práctica `('PR-01', None, 'sin tutor')`, correos `[]`. Código: `asignar_tutor.py:56-58`, `src/infraestructura/controlador_rest.py:26` |
| ESC-SR Usuario sin rol CoordinadorPracticas | Cumple | `HTTP 403 {'codigo': 'acceso_denegado', …}`. Práctica `('PR-01', None, 'sin tutor')`. Bitácora: `{'usuario': 'T-200', 'rol': 'Tutor', 'recurso': 'practica:PR-01', 'accion': 'asignar tutor', 'hora': …}`. Código: `asignar_tutor.py:45-54` |
| ESC-TV Token emitido hace 16 minutos | Cumple | `HTTP 401 {'codigo': 'no_autenticado', …}`. Práctica `('PR-01', None, 'sin tutor')`, bitácora `[]`. Código: `controlador_rest.py:108` (valida el token antes del caso de uso), `src/infraestructura/proveedor_identidad_simulado.py:9,30` |

Los resultados "no asignada" no escriben en la bitácora ni envían correos, como decidió la spec. Todas las respuestas de error llevan `codigo`, `mensaje` y `correlacion`.

## Validación arquitectónica

- **Regla de dependencia: cumple.** `src/dominio/` solo importa `dataclasses`, `datetime`, `enum`, `re` y módulos de `dominio`. Ningún archivo de `src/aplicacion/` importa `infraestructura`.
- **Vista de usos sin ciclos: cumple.** El Módulo Asignación (`src/aplicacion/asignacion/`) usa el Módulo Configuración (`src/aplicacion/configuracion/consultar_regla_vigente.py`) para la carga máxima, y Configuración no usa otros módulos.
- **Cada ADR del plan se ve en el código:**
  - ADR-002: caso de uso en el Módulo Asignación; puertos `Notificador` y `RepositorioPracticas` como `Protocol` en `src/aplicacion/puertos/`; `src/main.py` es la única composición (`main.py:32-46`).
  - ADR-003: el adaptador en memoria implementa los métodos nuevos del puerto (`repositorio_practicas_memoria.py:83-131`).
  - ADR-004: la autorización por rol está en el caso de uso (`asignar_tutor.py:45`), no en el controlador.
  - ADR-006: se audita cada cambio de estado de Práctica (`asignar_tutor.py:90-96`) y cada acceso rechazado (`:47-53`), con usuario, rol, recurso, acción y hora.
  - ADR-007: errores `TutorNoEncontrado` y `CorreoNoEnviado` en `src/aplicacion/errores/`. El adaptador de correo traduce su falla a `CorreoNoEnviado` y deja el correo pendiente; la asignación no se revierte (`asignar_tutor.py:117`).
  - ADR-008: la carga máxima es un dato de `ReglaPractica` (`src/dominio/regla_practica.py`), precargado en `main.py:53-55`; cambiarlo a "v2" no exige programar (ESC-RV).
- **Convenciones de AGENTS.md: cumplen.** Python 3.12 (`StrEnum`, `str | None`). Una clase por archivo en todo `src/`. Cero `__init__.py` y ningún archivo con BOM. DTO `SolicitudAsignacionTutor` en la entrada y `AsignacionRealizada`/`ResultadoPractica` en la salida; `ReglaVigente` en la salida de `ConsultarReglaVigente`. Nombres del glosario (`Practica`, `EstadoPractica`, `Tutor`, `Estudiante`, `ReglaPractica`, `Notificador`, `Bitacora`). Solo librería estándar.

### Observaciones (no se corrigen en esta fase)

1. **CU-01 y CU-02 no se rompieron.** Los scripts de los Anexos de [001/validacion.md](../001-postularse-plaza-practica/validacion.md) y [002/validacion.md](../002-publicar-plaza-practica/validacion.md) se volvieron a ejecutar contra este `src/` con los mismos resultados (201, 409, 404, 403 con su registro de bitácora, 401 y `[201, 201]` en CU-01; 201, 404, 400, 403 y 401 en CU-02).
2. **Horas requeridas de la regla "v1":** `main.py` precarga 160 horas como dato de prueba; CU-03 no las usa. El valor real lo fija el Coordinador (ADR-008).
3. **Estado intermedio entre commits:** entre `003 T-18` y `003 T-19`, `main.py` construía `ControladorRest` con tres argumentos. Es consecuencia del orden de adentro hacia afuera; `003 T-19` lo resolvió.
4. **Auditoría de los obreros:** en T-03 el docstring de `Tutor.tiene_cupo` quedó con comillas simples, en T-04 faltaban las líneas en blanco de PEP 8 y en T-15 faltaba el docstring de `ejecutar`; se corrigieron antes de cada commit. Varios archivos llegaron sin salto de línea final y se completaron.

## Anexo: script de ejecución

```python
"""Ejecuta los escenarios de specs/003 contra la composicion de src/main.py."""
import sys
from datetime import datetime, timedelta
sys.path.insert(0, sys.argv[1])
from main import construir
from dominio.estado_practica import EstadoPractica
from dominio.practica import Practica
from dominio.regla_practica import ReglaPractica


def app():
    a = construir()
    return a, a["controlador"], a["repositorio"], a["bitacora"], a["notificador"]


def ver(repo, *ids):
    return [(p.id, p.id_tutor, str(p.estado)) for i in ids if (p := repo.obtener_practica(i))]


def carga(repo, t):
    return repo.contar_practicas_activas_tutor(t)


def ocupar(repo, tutor, n, estado=EstadoPractica.EN_CURSO, prefijo="PX"):
    for k in range(n):
        repo.agregar_practica(Practica(f"{prefijo}-{k}", f"E-9{k}", "EMP-ACME", "v1", estado, tutor))


def asignar(c, ids, tutor="T-200", token="tok-C-01"):
    return c.asignar_tutor(token, {"id_tutor": tutor, "ids_practicas": ids})


print("== ESC-B")
a, c, r, b, n = app()
print(" carga antes:", carga(r, "T-200"))
print(" HTTP", *asignar(c, ["PR-01"]))
print(" practica:", ver(r, "PR-01"), "carga:", carga(r, "T-200"))
print(" bitacora:", b.listar())
print(" correos:", n.listar_enviados())

print("== ESC-VA")
a, c, r, b, n = app()
print(" HTTP", *asignar(c, ["PR-01", "PR-02"]))
print(" practicas:", ver(r, "PR-01", "PR-02"), "carga:", carga(r, "T-200"))
print(" bitacora:", [(x["recurso"], x["accion"]) for x in b.listar()])

print("== ESC-SC")
a, c, r, b, n = app()
ocupar(r, "T-200", 2)
print(" carga antes:", carga(r, "T-200"))
print(" HTTP", *asignar(c, ["PR-01"]))
print(" practica:", ver(r, "PR-01"), "carga:", carga(r, "T-200"))
print(" bitacora:", b.listar(), "correos:", n.listar_enviados())

print("== ESC-CE")
a, c, r, b, n = app()
ocupar(r, "T-200", 1)
ocupar(r, "T-200", 1, EstadoPractica.CERRADA, "PC")
print(" carga antes (activas):", carga(r, "T-200"))
print(" HTTP", *asignar(c, ["PR-01"]))
print(" practica:", ver(r, "PR-01"))

print("== ESC-CP")
a, c, r, b, n = app()
ocupar(r, "T-200", 1)
print(" HTTP", *asignar(c, ["PR-01", "PR-02"]))
print(" practicas:", ver(r, "PR-01", "PR-02"), "carga:", carga(r, "T-200"))

print("== ESC-CO")
a, c, r, b, n = app()
n.disponible = False
print(" HTTP", *asignar(c, ["PR-01"]))
print(" practica:", ver(r, "PR-01"))
print(" enviados:", n.listar_enviados(), "pendientes:", n.listar_pendientes())

print("== ESC-RV")
a, c, r, b, n = app()
ocupar(r, "T-200", 2)
r.agregar_regla(ReglaPractica("v2", 160, 3, "plantilla-acta-v2"))
print(" regla vigente:", r.obtener_regla_vigente())
print(" HTTP", *asignar(c, ["PR-01"]))
print(" practica:", ver(r, "PR-01"), "carga:", carga(r, "T-200"))

print("== ESC-YT")
a, c, r, b, n = app()
print(" HTTP", *asignar(c, ["PR-03"]))
print(" practica:", ver(r, "PR-03"), "carga T-200:", carga(r, "T-200"))

print("== ESC-PN")
a, c, r, b, n = app()
print(" HTTP", *asignar(c, ["PR-99"]))
print(" carga T-200:", carga(r, "T-200"))

print("== ESC-TN")
a, c, r, b, n = app()
print(" HTTP", *asignar(c, ["PR-01"], tutor="T-999"))
print(" practica:", ver(r, "PR-01"), "correos:", n.listar_enviados())

print("== ESC-SR")
a, c, r, b, n = app()
print(" HTTP", *asignar(c, ["PR-01"], token="tok-T-200"))
print(" practica:", ver(r, "PR-01"))
print(" bitacora:", b.listar())

print("== ESC-TV")
a, c, r, b, n = app()
a["proveedor"].emitir("tok-C-vencido", "C-01", "CoordinadorPracticas", datetime.now() - timedelta(minutes=16))
print(" HTTP", *asignar(c, ["PR-01"], token="tok-C-vencido"))
print(" practica:", ver(r, "PR-01"), "bitacora:", b.listar())
```
