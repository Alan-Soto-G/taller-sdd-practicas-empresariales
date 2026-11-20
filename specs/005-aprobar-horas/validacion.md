# Validación: 005 Aprobar horas reportadas

Fecha: 2026-11-20. Código validado: `src/` en el commit `95eae8b` (005 T-11).

Método: cada escenario se ejecutó contra la composición real de `src/main.py` (`construir()`), con una aplicación nueva por escenario y los datos de los Antecedentes de [spec.md](spec.md): ReglaPractica "v1" (160 horas), Tutor "T-300" (`tok-T-300`), Practica "PR-05" de "E-1005" "en curso" y el RegistroHoras "RH-05" (20 horas, "reportado"). Las 140 horas aprobadas previas se agregan como 7 registros "aprobados" de 20 horas, y la regla "v2" con `agregar_regla`. El script está en el Anexo. Se ejecuta con `python -B validar_cu05.py <ruta>/src`.

## Validación funcional

| Escenario | Resultado | Evidencia |
|-----------|-----------|-----------|
| ESC-B Flujo básico | Cumple | Antes `RH-05=reportado horas_aprobadas=0 PR-05=en curso`. `HTTP 200 {'id': 'RH-05', 'id_practica': 'PR-05', 'estado': 'aprobado', 'horas_aprobadas': 20, 'estado_practica': 'en curso', 'mensaje': 'horas aprobadas'}`. Después `RH-05=aprobado horas_aprobadas=20 PR-05=en curso`. Bitácora: `{'usuario': 'T-300', 'rol': 'Tutor', 'recurso': 'registro_horas:RH-05', 'accion': 'cambiar estado de reportado a aprobado', 'hora': …}`. Código: `src/aplicacion/horas/aprobar_horas.py:61-73`, `src/dominio/registro_horas.py:56-60` |
| ESC-RE Rechazo | Cumple | `HTTP 200 {… 'estado': 'rechazado', 'horas_aprobadas': 0, …, 'mensaje': 'horas rechazadas'}`. Después `RH-05=rechazado horas_aprobadas=0`. Bitácora `('T-300', 'registro_horas:RH-05', 'cambiar estado de reportado a rechazado')`. Código: `registro_horas.py:62-66` |
| ESC-HC Completa las horas requeridas | Cumple | Antes `horas_aprobadas=140 PR-05=en curso`. `HTTP 200 {… 'horas_aprobadas': 160, 'estado_practica': 'horas completas', …}`. Bitácora: `('registro_horas:RH-05', 'cambiar estado de reportado a aprobado')` y `('practica:PR-05', 'cambiar estado de en curso a horas completas')`. Código: `aprobar_horas.py:75-89`, `src/dominio/practica.py:25-29` |
| ESC-VR Versión de la práctica (ADR-008) | Cumple | Vigente `v2` con 200 horas; la práctica usa `v1` con 160. Con 140 aprobadas: `HTTP 200 {… 'horas_aprobadas': 160, 'estado_practica': 'horas completas', …}`. Código: `aprobar_horas.py:79` (`practica.version_regla`), `src/aplicacion/configuracion/consultar_horas_requeridas.py` |
| ESC-YR ya aprobado | Cumple | `HTTP 422 {'codigo': 'registro_no_valido', 'mensaje': 'registro no válido', …, 'motivo': 'el registro ya fue revisado'}`; sigue `RH-05=aprobado`. Código: `aprobar_horas.py:58-59` |
| ESC-YR ya rechazado | Cumple | `HTTP 422 … 'motivo': 'el registro ya fue revisado'`; sigue `RH-05=rechazado` |
| ESC-DI Decisión "pendiente" | Cumple | `HTTP 422 … 'motivo': 'la decisión debe ser aprobar o rechazar'`; sigue `RH-05=reportado`; bitácora `[]`. Código: `aprobar_horas.py:55-56` |
| ESC-RN Registro inexistente | Cumple | `HTTP 404 {'codigo': 'registro_no_encontrado', 'mensaje': 'registro de horas no encontrado', …}`. Código: `aprobar_horas.py:47-49`, `src/infraestructura/controlador_rest.py:35` |
| ESC-AJ EAC-04 tutor no asignado (T-200) | Cumple | `HTTP 403 {'codigo': 'acceso_denegado', …}`; sigue `RH-05=reportado`. Bitácora: `{'usuario': 'T-200', 'rol': 'Tutor', 'recurso': 'registro_horas:RH-05', 'accion': 'aprobar horas', 'hora': …}`, con usuario, recurso y hora (medida de EAC-04). Código: `aprobar_horas.py:51-53`, `:99-113` |
| ESC-ET Estudiante titular (E-1005) | Cumple | `HTTP 403 {'codigo': 'acceso_denegado', …}`; sigue `RH-05=reportado`. Bitácora: `{'usuario': 'E-1005', 'rol': 'Estudiante', 'recurso': 'registro_horas:RH-05', 'accion': 'aprobar horas', 'hora': …}`. Código: `aprobar_horas.py:44-45` |
| ESC-TV Token de hace 16 minutos | Cumple | `HTTP 401 {'codigo': 'no_autenticado', …}`; sigue `RH-05=reportado`; bitácora `[]` |

## Validación arquitectónica

- **Regla de dependencia: cumple.** `src/dominio/` solo importa la librería estándar y módulos de `dominio`. Ningún archivo de `src/aplicacion/` importa `infraestructura`.
- **Vista de usos sin ciclos: cumple.** El Módulo Horas usa el Módulo Configuración (`ConsultarHorasRequeridas`), y Configuración no usa otros módulos.
- **Cada ADR del plan se ve en el código:**
  - ADR-002: `AprobarHoras` en el Módulo Horas; composición en `main.py:45-49`.
  - ADR-003: el adaptador en memoria implementa `obtener_regla`, `obtener_registro_horas`, `actualizar_registro_horas` y `sumar_horas_aprobadas` (`repositorio_practicas_memoria.py:158-183`).
  - ADR-004: rol `Tutor` (`aprobar_horas.py:44`) y titularidad, es decir el tutor asignado (`:52`), en el caso de uso.
  - ADR-006: se auditan la aprobación o el rechazo (`aprobar_horas.py:67-73`), el paso a "horas completas" (`:83-89`) y cada acceso rechazado (`:106-112`).
  - ADR-007: `RegistroNoEncontrado` (404) y `RegistroNoValido` (422) en el controlador.
  - ADR-008: horas requeridas de la versión de la práctica (`aprobar_horas.py:79`).
- **Convenciones de AGENTS.md: cumplen.** Una clase por archivo, cero `__init__.py`, ningún archivo con BOM. DTO `SolicitudRevisionHoras` y `HorasRevisadas`. Nombres del glosario. Solo librería estándar.

### Observaciones (no se corrigen en esta fase)

1. **CU-01 a CU-04 no se rompieron.** Los scripts de los Anexos dan los mismos códigos: CU-01 `201, 409, 409, 201, 409, 409, 201, 404, 403, 401, [201, 201]`; CU-02 `201×3, 404, 400×5, 403, 401`; CU-03 los mismos resultados por práctica, más `404, 403, 401`; CU-04 `201, 201, 422×8, 404, 403, 403, 401`, `{201: 300}`, con 300 registros en 300 prácticas.
2. **Lectura del script de CU-04:** desde esta composición, la lista de registros que imprime el script de 004 cuando no filtra por práctica incluye el registro precargado "RH-05" de "PR-05". No es un registro nuevo y no cambia el resultado de 004: en esos escenarios "PR-04" sigue sin registros.
3. **Proceso:** en T-09, agy escribió el cambio completo pero no terminó; se detuvo la tarea y el diff se auditó antes del commit.

## Anexo: script de ejecución

```python
"""Ejecuta los escenarios de specs/005 contra la composicion de src/main.py."""
import sys
from datetime import date, datetime, timedelta
sys.path.insert(0, sys.argv[1])
from main import construir
from dominio.estado_registro_horas import EstadoRegistroHoras
from dominio.registro_horas import RegistroHoras
from dominio.regla_practica import ReglaPractica


def app():
    a = construir()
    return a, a["controlador"], a["repositorio"], a["bitacora"]


def estado(r):
    reg = r.obtener_registro_horas("RH-05")
    p = r.obtener_practica("PR-05")
    return f"RH-05={reg.estado} horas_aprobadas={r.sumar_horas_aprobadas('PR-05')} PR-05={p.estado}"


def con_140_aprobadas(r):
    for k in range(7):
        r.guardar_registro_horas(RegistroHoras(f"RA-{k}", "PR-05", f"2026-W{30 + k}", 20, "Trabajo",
                                               date(2026, 8, 1), EstadoRegistroHoras.APROBADO))


def revisar(c, token="tok-T-300", id_registro="RH-05", decision="aprobar"):
    return c.revisar_horas(token, id_registro, {"decision": decision})


print("== ESC-B")
a, c, r, b = app()
print(" antes:", estado(r))
print(" HTTP", *revisar(c))
print(" despues:", estado(r))
print(" bitacora:", b.listar())

print("== ESC-RE")
a, c, r, b = app()
print(" HTTP", *revisar(c, decision="rechazar"))
print(" despues:", estado(r))
print(" bitacora:", [(x["usuario"], x["recurso"], x["accion"]) for x in b.listar()])

print("== ESC-HC")
a, c, r, b = app()
con_140_aprobadas(r)
print(" antes:", estado(r))
print(" HTTP", *revisar(c))
print(" despues:", estado(r))
print(" bitacora:", [(x["recurso"], x["accion"]) for x in b.listar()])

print("== ESC-VR")
a, c, r, b = app()
r.agregar_regla(ReglaPractica("v2", 200, 2, "plantilla-acta-v2"))
con_140_aprobadas(r)
print(" vigente:", r.obtener_regla_vigente().version, r.obtener_regla_vigente().horas_requeridas,
      "| practica:", r.obtener_practica("PR-05").version_regla, r.obtener_regla("v1").horas_requeridas)
print(" HTTP", *revisar(c))
print(" despues:", estado(r))

for previo in ("aprobar", "rechazar"):
    print(f"== ESC-YR (previo {previo})")
    a, c, r, b = app()
    revisar(c, decision=previo)
    print(" antes:", estado(r))
    print(" HTTP", *revisar(c))
    print(" despues:", estado(r))

print("== ESC-DI")
a, c, r, b = app()
print(" HTTP", *revisar(c, decision="pendiente"))
print(" despues:", estado(r), "bitacora:", b.listar())

print("== ESC-RN")
a, c, r, b = app()
print(" HTTP", *revisar(c, id_registro="RH-99"))

print("== ESC-AJ")
a, c, r, b = app()
print(" HTTP", *revisar(c, token="tok-T-200"))
print(" despues:", estado(r))
print(" bitacora:", b.listar())

print("== ESC-ET")
a, c, r, b = app()
print(" HTTP", *revisar(c, token="tok-E-1005"))
print(" despues:", estado(r))
print(" bitacora:", b.listar())

print("== ESC-TV")
a, c, r, b = app()
a["proveedor"].emitir("tok-T-300-vencido", "T-300", "Tutor", datetime.now() - timedelta(minutes=16))
print(" HTTP", *revisar(c, token="tok-T-300-vencido"))
print(" despues:", estado(r), "bitacora:", b.listar())
```
