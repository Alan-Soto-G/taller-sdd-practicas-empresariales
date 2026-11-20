# Validación: 006 Evaluar el desempeño del practicante

Fecha: 2026-11-20. Código validado: `src/` en el commit `20c527d` (006 T-25).

Método: cada escenario se ejecutó contra la composición real de `src/main.py` (`construir()`), con una aplicación nueva por escenario y los datos de los Antecedentes de [spec.md](spec.md):
- ReglaPractica "v1" con tres criterios de escala 5;
- RepresentanteEmpresa "R-01" de "EMP-ACME";
- Practica "PR-06" en "horas completas";
- Coordinador "C-01" (`tok-C-01`).

El token del enlace se lee del repositorio en memoria (en producción solo viaja por correo). El enlace vencido se crea con `EnlaceAcceso.emitir` hace 8 días, y la regla "v2" y la Practica "PR-07" de EAC-03 se agregan como datos. El script está en el Anexo. Se ejecuta con `python -B validar_cu06.py <ruta>/src`.

## Validación funcional

| Escenario | Resultado | Evidencia |
|-----------|-----------|-----------|
| ESC-B1 Emitir el enlace | Cumple | `HTTP 201 {'id_enlace': 'EN-f23d902b', 'id_practica': 'PR-06', 'vence': '2026-11-27T08:37:54…', 'correo_representante': 'representante@acme.example', 'mensaje': 'enlace de evaluación enviado'}`. Enlaces `[('EN-f23d902b', 'PR-06', 'evaluar', False)]`, vence a los `7 days`. Correo a `['representante@acme.example']`: "Evalúe a su practicante en /evaluaciones/<token>; el enlace vence el 2026-11-27." Código: `src/aplicacion/evaluacion/emitir_enlace_evaluacion.py:72-97`, `src/dominio/enlace_acceso.py:6,22` |
| ESC-B2 Abrir el formulario | Cumple | `HTTP 200 {'id_practica': 'PR-06', 'id_estudiante': 'E-1006', 'criterios': [{'nombre': 'Responsabilidad', 'escala': 5}, {'nombre': 'Trabajo en equipo', 'escala': 5}, {'nombre': 'Calidad técnica', 'escala': 5}]}`. Enlace usado: `False`. Código: `src/infraestructura/controlador_rest.py:254-274`, `src/aplicacion/evaluacion/consultar_formulario_evaluacion.py` |
| ESC-B3 Enviar la evaluación | Cumple | `HTTP 201 {'id': 'EV-d8e01999', 'id_practica': 'PR-06', 'estado_practica': 'evaluada', 'mensaje': 'evaluación enviada'}`. Evaluación `('PR-06', {'Responsabilidad': 5, 'Trabajo en equipo': 4, 'Calidad técnica': 5}, 'Muy buen desempeño')`. Enlace usado `True`; PR-06 `evaluada`. Bitácora: `('R-01', 'RepresentanteEmpresa', 'enlace', 'usar enlace de evaluación')`, `(…, 'evaluacion', 'crear evaluación')`, `(…, 'practica', 'cambiar estado de horas completas a evaluada')`. Código: `src/aplicacion/evaluacion/registrar_evaluacion.py:56-85` |
| ESC-HC Sin horas completas (PR-04) | Cumple | `HTTP 409 {'codigo': 'evaluacion_no_permitida', 'mensaje': 'evaluación no permitida', …, 'motivo': 'la práctica no tiene las horas completas'}`. Enlaces `[]`. Código: `emitir_enlace_evaluacion.py:61-62` |
| ESC-SR Sin rol Coordinador (T-300) | Cumple | `HTTP 403 {'codigo': 'acceso_denegado', …}`. Enlaces `[]`. Bitácora `{'usuario': 'T-300', 'rol': 'Tutor', 'recurso': 'practica:PR-06', 'accion': 'emitir enlace de evaluación', 'hora': …}`. Código: `emitir_enlace_evaluacion.py:47-55` |
| ESC-TV Token de hace 16 minutos | Cumple | `HTTP 401 {'codigo': 'no_autenticado', …}`. Enlaces `[]` |
| ESC-RE Reemitir | Cumple | Enlaces `[('EN-8accdbca', True), ('EN-30813b52', False)]`, el nuevo es distinto. Abrir el anterior: `HTTP 410 {'codigo': 'enlace_no_valido', 'mensaje': 'enlace vencido: solicite uno nuevo a la Coordinación', …, 'motivo': 'enlace usado'}`. Abrir el nuevo: `HTTP 200`. Código: `emitir_enlace_evaluacion.py:72-74`, `src/infraestructura/repositorio_practicas_memoria.py:220-229` |
| ESC-CO Falla el correo | Cumple | `HTTP 201 {… 'mensaje': 'enlace de evaluación enviado'}`. Enlaces `[('PR-06', False)]`; enviados `[]`; pendientes `[['representante@acme.example']]`. Código: `emitir_enlace_evaluacion.py:85-93` |
| ESC-EV enlace vencido | Cumple | `HTTP 410 {… 'motivo': 'enlace vencido'}`. PR-06 `horas completas`. Bitácora nueva `('R-01', 'RepresentanteEmpresa', 'enlace:EN-viejo', 'usar enlace rechazado: enlace vencido')`. Código: `src/infraestructura/validador_enlace.py:27-52`, `enlace_acceso.py:24-32` |
| ESC-EV enlace usado | Cumple | `HTTP 410 {… 'motivo': 'enlace usado'}`. PR-06 sigue `evaluada` (el uso anterior la evaluó; el intento no la cambia). Bitácora nueva `('R-01', 'RepresentanteEmpresa', 'enlace:EN-3eeb61fa', 'usar enlace rechazado: enlace usado')` |
| ESC-EV enlace inexistente | Cumple | `HTTP 410 {… 'motivo': 'enlace inválido'}`. PR-06 `horas completas`. Bitácora nueva `('desconocido', 'RepresentanteEmpresa', 'enlace:desconocido', 'usar enlace rechazado: enlace inválido')`. Código: `validador_enlace.py:31-32` |
| ESC-CI falta un criterio | Cumple | `HTTP 422 {'codigo': 'evaluacion_no_valida', 'mensaje': 'evaluación no válida', …, 'motivo': 'falta calificar el criterio Calidad técnica'}`. Evaluaciones `[]`, enlace usado `False`. Código: `src/dominio/evaluacion.py:16-28`, `registrar_evaluacion.py:53-54` |
| ESC-CI calificación 6 | Cumple | `HTTP 422 … 'motivo': 'la calificación de Responsabilidad debe estar entre 1 y 5'`. Evaluaciones `[]`, enlace usado `False` |
| ESC-CI calificación 0 | Cumple | `HTTP 422 … 'motivo': 'la calificación de Responsabilidad debe estar entre 1 y 5'`. Evaluaciones `[]`, enlace usado `False` |
| ESC-CI criterio desconocido | Cumple | `HTTP 422 … 'motivo': 'criterio desconocido: Puntualidad'`. Evaluaciones `[]`, enlace usado `False` |
| ESC-E5 Sin cuenta ni instalación | Cumple (parte comprobable) | 2 peticiones del Representante, `[200, 201]`, y 1 evaluación registrada. `abrir_evaluacion(enlace)` y `enviar_evaluacion(enlace, cuerpo)` no reciben token institucional (`controlador_rest.py:254,276`). La medida de menos de 5 minutos para el 90% se toma en la prueba de usuario, fuera de las specs |
| ESC-E3 Criterio nuevo como dato | Cumple | Con la regla "v2" agregada como dato: el formulario de PR-07 tiene 4 criterios, `['Responsabilidad', 'Trabajo en equipo', 'Calidad técnica', 'Comunicación']`, y el de PR-06 ("v1") sigue con 3. La huella SHA-256 de `src/` es `8bf513e74f964594` antes y después: no se cambió código |

## Validación arquitectónica

- **Regla de dependencia: cumple.** `src/dominio/` solo importa la librería estándar y módulos de `dominio`. Ningún archivo de `src/aplicacion/` importa `infraestructura`.
- **Vista de usos sin ciclos: cumple.** El Módulo Evaluación usa el Módulo Configuración (`ConsultarCriteriosEvaluacion`), y Configuración no usa otros módulos.
- **Cada ADR del plan se ve en el código:**
  - ADR-002: Módulo Evaluación en `src/aplicacion/evaluacion/`; puertos como `Protocol`; composición en `main.py`.
  - ADR-003: `marcar_enlace_usado` es atómico con `Lock` (`repositorio_practicas_memoria.py:231-238`).
  - ADR-004: la autorización del Coordinador está en el caso de uso (`emitir_enlace_evaluacion.py:47`).
  - ADR-005: el Validador de enlace entrega `IdentidadEnlace` (práctica y acción) y no pide token institucional; el enlace vence a los 7 días (`enlace_acceso.py:6`), es de un solo uso (`registrar_evaluacion.py:56-57`) y se invalida al reemitirlo.
  - ADR-006: se auditan el uso del enlace, la evaluación, el cambio de estado (`registrar_evaluacion.py:71-82`), el acceso rechazado y cada intento con un enlace no válido (`validador_enlace.py:43-52`).
  - ADR-007: 410, 409 y 422 con motivo en `controlador_rest.py:50-52`; si el correo falla, el enlace no se revierte.
  - ADR-008: los criterios son datos de la versión de la regla de la práctica (`registrar_evaluacion.py:48-52`, ESC-E3).
- **Desviación declarada en el plan:** el Validador de enlace recibe el puerto `Bitacora` además de RepositorioPracticas, que es lo que nombra la vista de desarrollo. Lo exigen ADR-005 ("cada intento con un enlace vencido o inválido se audita") y la secuencia ESC-04 ("registra el intento rechazado"). No es un componente nuevo.
- **Convenciones de AGENTS.md: cumplen.** Una clase por archivo, cero `__init__.py`, ningún archivo con BOM; en el índice de git todo está en LF. DTO en la entrada y la salida de los casos de uso. Nombres del glosario (`EnlaceAcceso`, `Evaluacion`, `CriterioEvaluacion`, `RepresentanteEmpresa`). Solo librería estándar (`secrets` para el token).

### Observaciones

1. **Corrección de la spec en esta tarea:** en el esquema ESC-EV, la línea "la Practica PR-06 sigue en estado horas completas" no podía cumplirse en el ejemplo "ya se usó para enviar la evaluación", porque ese uso la deja "evaluada". Se cambió por "la Practica PR-06 no cambia de estado", que es lo que la regla exige (el intento rechazado no cambia nada). El comportamiento del código no cambió.
2. **CU-01 a CU-05 no se rompieron.** Los scripts de los Anexos dan los mismos códigos: CU-01 `201, 409, 409, 201, 409, 409, 201, 404, 403, 401, [201, 201]`; CU-02 `201×3, 404, 400×5, 403, 401`; CU-03 `200×9, 404, 403, 401`; CU-04 `201, 201, 422×8, 404, 403, 403, 401, {201: 300}`; CU-05 `200×4, 422×3, 404, 403, 403, 401`.
3. **Datos de prueba:** las prácticas precargadas no pasan por CU-03, así que el Tutor "T-300" tiene 3 prácticas activas (PR-03, PR-04 y PR-05) con carga máxima 2. No afecta a ningún escenario: la carga solo se revisa al asignar, y los escenarios de CU-03 usan "T-200". Para PR-06 se usa el Tutor "T-400".
4. **Proceso:** en T-17, agy se quedó colgado sin escribir el archivo; la tarea pasó a copilot (protocolo de fallback). Algunos obreros escriben con CRLF; `git` lo normaliza a LF en el índice.

## Anexo: script de ejecución

```python
"""Ejecuta los escenarios de specs/006 contra la composicion de src/main.py."""
import hashlib
import pathlib
import sys
from datetime import datetime, timedelta
sys.path.insert(0, sys.argv[1])
from main import construir
from dominio.criterio_evaluacion import CriterioEvaluacion
from dominio.enlace_acceso import EnlaceAcceso
from dominio.estado_practica import EstadoPractica
from dominio.estudiante import Estudiante
from dominio.practica import Practica
from dominio.regla_practica import ReglaPractica

VALIDAS = {"Responsabilidad": 5, "Trabajo en equipo": 4, "Calidad técnica": 5}


def app():
    a = construir()
    return a, a["controlador"], a["repositorio"], a["bitacora"], a["notificador"]


def enlaces(r):
    return [(e.id, e.id_practica, e.accion, e.usado, str(e.vence - datetime.now())[:6]) for e in r.listar_enlaces()]


def emitir(c, r, token="tok-C-01", practica="PR-06"):
    respuesta = c.emitir_enlace_evaluacion(token, practica)
    enlace = next((e for e in r.listar_enlaces() if not e.usado and e.id_practica == practica), None)
    return respuesta, enlace


def huella_src():
    h = hashlib.sha256()
    for p in sorted(pathlib.Path(sys.argv[1]).rglob("*.py")):
        h.update(p.read_bytes())
    return h.hexdigest()[:16]


print("== ESC-B1")
a, c, r, b, n = app()
(resp, enlace) = emitir(c, r)
print(" HTTP", *resp)
print(" enlaces:", [(e.id, e.id_practica, e.accion, e.usado) for e in r.listar_enlaces()],
      "vence - emitido:", enlace.vence.date() - datetime.now().date())
print(" correos:", [(x["destinatarios"], x["mensaje"].replace(enlace.token, "<token>")) for x in n.listar_enviados()])

print("== ESC-B2")
a, c, r, b, n = app()
_, enlace = emitir(c, r)
print(" HTTP", *c.abrir_evaluacion(enlace.token))
print(" enlace usado:", r.obtener_enlace_por_token(enlace.token).usado)

print("== ESC-B3")
a, c, r, b, n = app()
_, enlace = emitir(c, r)
print(" HTTP", *c.enviar_evaluacion(enlace.token, {"calificaciones": VALIDAS, "observaciones": "Muy buen desempeño"}))
print(" evaluaciones:", [(e.id_practica, e.calificaciones, e.observaciones) for e in r.listar_evaluaciones()])
print(" enlace usado:", r.obtener_enlace_por_token(enlace.token).usado, "| PR-06:", r.obtener_practica("PR-06").estado)
print(" bitacora:", [(x["usuario"], x["rol"], x["recurso"].split(":")[0], x["accion"]) for x in b.listar()])

print("== ESC-HC")
a, c, r, b, n = app()
print(" HTTP", *c.emitir_enlace_evaluacion("tok-C-01", "PR-04"))
print(" enlaces:", r.listar_enlaces())

print("== ESC-SR")
a, c, r, b, n = app()
print(" HTTP", *c.emitir_enlace_evaluacion("tok-T-300", "PR-06"))
print(" enlaces:", r.listar_enlaces(), "bitacora:", b.listar())

print("== ESC-TV")
a, c, r, b, n = app()
a["proveedor"].emitir("tok-C-vencido", "C-01", "CoordinadorPracticas", datetime.now() - timedelta(minutes=16))
print(" HTTP", *c.emitir_enlace_evaluacion("tok-C-vencido", "PR-06"))
print(" enlaces:", r.listar_enlaces())

print("== ESC-RE")
a, c, r, b, n = app()
_, viejo = emitir(c, r)
_, nuevo = emitir(c, r)
print(" enlaces:", [(e.id, e.usado) for e in r.listar_enlaces()], "nuevo distinto:", nuevo.id != viejo.id)
print(" abrir el anterior: HTTP", *c.abrir_evaluacion(viejo.token))
print(" abrir el nuevo: HTTP", c.abrir_evaluacion(nuevo.token)[0])

print("== ESC-CO")
a, c, r, b, n = app()
n.disponible = False
print(" HTTP", *c.emitir_enlace_evaluacion("tok-C-01", "PR-06"))
print(" enlaces:", [(e.id_practica, e.usado) for e in r.listar_enlaces()], "enviados:", n.listar_enviados(),
      "pendientes:", [x["destinatarios"] for x in n.listar_pendientes()])

for caso in ("vencido", "usado", "inexistente"):
    print(f"== ESC-EV ({caso})")
    a, c, r, b, n = app()
    if caso == "vencido":
        e = EnlaceAcceso.emitir("EN-viejo", "token-viejo", "PR-06", "R-01", "evaluar", datetime.now() - timedelta(days=8))
        r.guardar_enlace(e)
        token = e.token
    elif caso == "usado":
        _, e = emitir(c, r)
        c.enviar_evaluacion(e.token, {"calificaciones": VALIDAS})
        r.guardar_practica(r.obtener_practica("PR-06"))
        token = e.token
    else:
        token = "no-existe"
    antes = len(b.listar())
    print(" HTTP", *c.abrir_evaluacion(token))
    print(" PR-06:", r.obtener_practica("PR-06").estado, "| bitacora nueva:",
          [(x["usuario"], x["rol"], x["recurso"], x["accion"]) for x in b.listar()[antes:]])

casos = [
    ({"Responsabilidad": 5, "Trabajo en equipo": 4}, "falta"),
    ({"Responsabilidad": 6, "Trabajo en equipo": 4, "Calidad técnica": 5}, "6"),
    ({"Responsabilidad": 0, "Trabajo en equipo": 4, "Calidad técnica": 5}, "0"),
    ({**VALIDAS, "Puntualidad": 5}, "desconocido"),
]
for calificaciones, nombre in casos:
    print(f"== ESC-CI ({nombre})")
    a, c, r, b, n = app()
    _, enlace = emitir(c, r)
    print(" HTTP", *c.enviar_evaluacion(enlace.token, {"calificaciones": calificaciones}))
    print(" evaluaciones:", r.listar_evaluaciones(), "enlace usado:", r.obtener_enlace_por_token(enlace.token).usado)

print("== ESC-E5")
a, c, r, b, n = app()
_, enlace = emitir(c, r)
pasos = [c.abrir_evaluacion(enlace.token)[0], c.enviar_evaluacion(enlace.token, {"calificaciones": VALIDAS})[0]]
print(" peticiones del Representante:", len(pasos), pasos, "| token institucional usado: ninguno (abrir_evaluacion y enviar_evaluacion solo reciben el enlace)")
print(" evaluaciones:", len(r.listar_evaluaciones()))

print("== ESC-E3")
antes = huella_src()
a, c, r, b, n = app()
r.agregar_regla(ReglaPractica("v2", 160, 2, "plantilla-acta-v2", (
    CriterioEvaluacion("Responsabilidad", 5), CriterioEvaluacion("Trabajo en equipo", 5),
    CriterioEvaluacion("Calidad técnica", 5), CriterioEvaluacion("Comunicación", 5))))
r.agregar_estudiante(Estudiante("E-1007", "e1007@universidad.edu.co"))
r.agregar_practica(Practica("PR-07", "E-1007", "EMP-ACME", "v2", EstadoPractica.HORAS_COMPLETAS, "T-400"))
_, e7 = emitir(c, r, practica="PR-07")
_, e6 = emitir(c, r, practica="PR-06")
f7 = c.abrir_evaluacion(e7.token)[1]["criterios"]
f6 = c.abrir_evaluacion(e6.token)[1]["criterios"]
print(" PR-07:", len(f7), [x["nombre"] for x in f7])
print(" PR-06:", len(f6), [x["nombre"] for x in f6])
print(" huella de src antes:", antes, "despues:", huella_src())
```
