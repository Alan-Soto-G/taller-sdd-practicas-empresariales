# Validación: 009 Consultar el avance de los estudiantes asignados

Fecha: 2026-11-20. Código validado: `src/` en el commit `9c34569` (009 T-10).

Método: cada escenario se ejecutó contra la composición real de `src/main.py` (`construir()`), con una aplicación nueva por escenario y los datos de los Antecedentes de [spec.md](spec.md):
- Tutor "T-500" (`tok-T-500`);
- "PR-10", con 3 registros aprobados de 20 horas y 1 reportado de 20;
- "PR-11", sin registros.

ESC-VR agrega como datos la regla "v2" (no vigente) y "PR-12". El script está en el Anexo. Se ejecuta con `python -B validar_cu09.py <ruta>/src`.

## Validación funcional

| Escenario | Resultado | Evidencia |
|-----------|-----------|-----------|
| ESC-B Avance de sus prácticas | Cumple | `HTTP 200 {'id_tutor': 'T-500', 'practicas': [{'id_practica': 'PR-10', 'id_estudiante': 'E-1010', 'estado': 'en curso', 'horas_aprobadas': 60, 'horas_requeridas': 160, 'horas_pendientes': 20, 'porcentaje': 37}, {'id_practica': 'PR-11', …, 'horas_aprobadas': 0, 'horas_requeridas': 160, 'horas_pendientes': 0, 'porcentaje': 0}]}`. Bitácora `[]`. Código: `src/aplicacion/seguimiento/consultar_avance_tutor.py`, `src/aplicacion/horas/resumir_horas_practica.py` |
| ESC-UNA Una sola práctica | Cumple | `HTTP 200` con solo `PR-10`: 60 de 160, 37% |
| ESC-VAC Tutor sin prácticas (T-200) | Cumple | `HTTP 200 {'id_tutor': 'T-200', 'practicas': []}` |
| ESC-VR Versión de la práctica (ADR-008) | Cumple | `PR-12` con la regla "v2": `'horas_aprobadas': 100, 'horas_requeridas': 200, 'porcentaje': 50` (la regla vigente sigue siendo "v1", de 160 horas) |
| ESC-AJ EAC-04, práctica ajena (PR-04) | Cumple | `HTTP 403 {'codigo': 'acceso_denegado', …}`. Bitácora `{'usuario': 'T-500', 'rol': 'Tutor', 'recurso': 'practica:PR-04', 'accion': 'consultar avance', 'hora': …}` |
| ESC-SR Sin rol Tutor (E-1010) | Cumple | `HTTP 403`. Bitácora `{'usuario': 'E-1010', 'rol': 'Estudiante', 'recurso': 'practica:PR-10', 'accion': 'consultar avance', 'hora': …}` |
| ESC-PN Práctica inexistente | Cumple | `HTTP 404 {'codigo': 'practica_no_encontrada', 'mensaje': 'práctica no encontrada', …}` |
| ESC-TV Token de hace 16 minutos | Cumple | `HTTP 401 {'codigo': 'no_autenticado', …}`; bitácora `[]` |

## Validación arquitectónica

- **Regla de dependencia: cumple.** `dominio/` no importa las otras capas y `aplicacion/` no importa `infraestructura/`.
- **Vista de usos: cumple.** Seguimiento (`src/aplicacion/seguimiento/`) usa el Módulo Horas (`ResumirHorasPractica`), y Horas usa Configuración (`ConsultarHorasRequeridas`). Seguimiento no usa Configuración directamente y no hay ciclos.
- **Cada ADR del plan se ve en el código:**
  - ADR-004: rol `Tutor` y titularidad en `consultar_avance_tutor.py`, no en el controlador.
  - ADR-006: solo se auditan los accesos rechazados; las consultas no se auditan.
  - ADR-007: 403 y 404 unificados.
  - ADR-008: horas requeridas de la versión de cada práctica (ESC-VR).
- **Convenciones de AGENTS.md: cumplen.** Una clase por archivo, sin `__init__.py`, sin BOM, DTO en la entrada y la salida, nombres del glosario.

### Observaciones

1. **CU-01 a CU-08 no se rompieron.** Los scripts de los Anexos dan los mismos códigos: CU-01 `201, 409, 409, 201, 409, 409, 201, 404, 403, 401, [201, 201]`; CU-02 `201×3, 404, 400×5, 403, 401`; CU-03 `200×9, 404, 403, 401`; CU-04 `201, 201, 422×8, 404, 403, 403, 401, {201: 300}`; CU-05 `200×4, 422×3, 404, 403, 403, 401`; CU-06 `201, 200, 201, 409, 403, 401, 410, 200, 201, 410×3, 422×4`; CU-07 `202×3, 403, 401, 202`, con 500 de 500 actas; CU-08 `201×4, 409×3, 404, 403×3, 410×3, 401`.
2. **Porcentaje:** se redondea hacia abajo (60 × 100 / 160 = 37,5 → 37), para no mostrar un avance mayor que el real.

## Anexo: script de ejecución

```python
"""Ejecuta los escenarios de specs/009 contra la composicion de src/main.py."""
import sys
from datetime import date, datetime, timedelta
sys.path.insert(0, sys.argv[1])
from main import construir
from dominio.estado_practica import EstadoPractica
from dominio.estado_registro_horas import EstadoRegistroHoras
from dominio.estudiante import Estudiante
from dominio.practica import Practica
from dominio.registro_horas import RegistroHoras
from dominio.regla_practica import ReglaPractica


def app():
    a = construir()
    return a, a["controlador"], a["repositorio"], a["bitacora"]


print("== ESC-B")
a, c, r, b = app()
print(" HTTP", *c.consultar_avance("tok-T-500"))
print(" bitacora:", b.listar())

print("== ESC-UNA")
a, c, r, b = app()
print(" HTTP", *c.consultar_avance("tok-T-500", "PR-10"))

print("== ESC-VAC")
a, c, r, b = app()
print(" HTTP", *c.consultar_avance("tok-T-200"))

print("== ESC-VR")
a, c, r, b = app()
r.agregar_regla(ReglaPractica("v2", 200, 2, "plantilla-acta-v2"), vigente=False)
r.agregar_estudiante(Estudiante("E-1012", "e1012@universidad.edu.co"))
r.agregar_practica(Practica("PR-12", "E-1012", "EMP-ACME", "v2", EstadoPractica.EN_CURSO, "T-500"))
for k in (1, 2):
    r.guardar_registro_horas(RegistroHoras(f"RH-12-{k}", "PR-12", f"2026-W0{k}", 50, "Trabajo", date(2026, 1, 9), EstadoRegistroHoras.APROBADO))
print(" HTTP", *c.consultar_avance("tok-T-500", "PR-12"))

print("== ESC-AJ")
a, c, r, b = app()
print(" HTTP", *c.consultar_avance("tok-T-500", "PR-04"))
print(" bitacora:", b.listar())

print("== ESC-SR")
a, c, r, b = app()
print(" HTTP", *c.consultar_avance("tok-E-1010", "PR-10"))
print(" bitacora:", b.listar())

print("== ESC-PN")
a, c, r, b = app()
print(" HTTP", *c.consultar_avance("tok-T-500", "PR-99"))

print("== ESC-TV")
a, c, r, b = app()
a["proveedor"].emitir("tok-T-vencido", "T-500", "Tutor", datetime.now() - timedelta(minutes=16))
print(" HTTP", *c.consultar_avance("tok-T-vencido"))
print(" bitacora:", b.listar())
```
