# Validación: 010 Consultar el estado de la práctica y del acta

Fecha: 2026-11-20. Código validado: `src/` en el commit `eef0286` (010 T-10). Implementado por Claude sin obreros, a pedido del usuario.

Método: cada escenario se ejecutó contra la composición real de `src/main.py` (`construir()`), con una aplicación nueva por escenario y los datos de los Antecedentes de [spec.md](spec.md), precargados por CU-07, CU-08 y CU-09: "PR-08" (`tok-E-1008`), "PR-09" con "AC-09" (`tok-E-1009`) y "PR-10" (`tok-E-1010`). El script está en el Anexo. Se ejecuta con `python -B validar_cu10.py <ruta>/src`.

## Validación funcional

| Escenario | Resultado | Evidencia |
|-----------|-----------|-----------|
| ESC-B Práctica evaluada (PR-08) | Cumple | `HTTP 200 {'id_estudiante': 'E-1008', 'practicas': [{'id_practica': 'PR-08', 'id_empresa': 'EMP-ACME', 'id_tutor': 'T-400', 'estado': 'evaluada', 'horas_aprobadas': 160, 'horas_requeridas': 160, 'horas_pendientes': 0, 'porcentaje': 100, 'evaluacion_registrada': True, 'acta': None}]}`. Bitácora `[]`. Código: `src/aplicacion/seguimiento/consultar_estado_practica.py` (`_consultar`) |
| ESC-EC En curso (PR-10) | Cumple | `'estado': 'en curso', 'horas_aprobadas': 60, 'horas_requeridas': 160, 'horas_pendientes': 20, 'porcentaje': 37, 'evaluacion_registrada': False, 'acta': None` |
| ESC-AC Acta esperando aprobaciones (PR-09) | Cumple | `'estado': 'acta en trámite'`, `'acta': {'id_acta': 'AC-09', 'estado': 'generada', 'aprobaciones': 0}`. Código: `src/aplicacion/actas/consultar_acta_practica.py` |
| ESC-TO Todas sus prácticas | Cumple | `HTTP 200`, prácticas `['PR-10']` |
| ESC-AJ EAC-04, práctica ajena | Cumple | `HTTP 403 {'codigo': 'acceso_denegado', …}`. Bitácora `{'usuario': 'E-1010', 'rol': 'Estudiante', 'recurso': 'practica:PR-08', 'accion': 'consultar estado', 'hora': …}`, con usuario, recurso y hora (medida de EAC-04) |
| ESC-SR Sin rol Estudiante (T-500) | Cumple | `HTTP 403`. Bitácora `{'usuario': 'T-500', 'rol': 'Tutor', 'recurso': 'practica:PR-10', 'accion': 'consultar estado', 'hora': …}` |
| ESC-PN Práctica inexistente | Cumple | `HTTP 404 {'codigo': 'practica_no_encontrada', …}` |
| ESC-TV Token de hace 16 minutos | Cumple | `HTTP 401 {'codigo': 'no_autenticado', …}` |

## Validación arquitectónica

- **Regla de dependencia: cumple.** `dominio/` no importa las otras capas y `aplicacion/` no importa `infraestructura/`.
- **Vista de usos: cumple.** Seguimiento usa el Módulo Horas (`ResumirHorasPractica`) y el Módulo Actas (`ConsultarActaPractica`), ambos en solo lectura. Actas y Horas no usan Seguimiento.
- **ADR:**
  - ADR-004: rol Estudiante y titularidad en el caso de uso.
  - ADR-006: se auditan solo los accesos rechazados.
  - ADR-007: 403 y 404 unificados.
  - ADR-008: horas requeridas por versión, a través del Módulo Horas.
- **Convenciones de AGENTS.md: cumplen.** Una clase por archivo, sin `__init__.py`, sin BOM, DTO en la entrada y la salida.

### Observaciones

1. **CU-01 a CU-09 no se rompieron.** Los scripts de los Anexos dan los mismos códigos: CU-01 `201, 409, 409, 201, 409, 409, 201, 404, 403, 401, [201, 201]`; CU-02 `201×3, 404, 400×5, 403, 401`; CU-03 `200×9, 404, 403, 401`; CU-04 `201, 201, 422×8, 404, 403, 403, 401, {201: 300}`; CU-05 `200×4, 422×3, 404, 403, 403, 401`; CU-06 `201, 200, 201, 409, 403, 401, 410, 200, 201, 410×3, 422×4`; CU-07 `202×3, 403, 401, 202` con 500 de 500 actas; CU-08 `201×4, 409×3, 404, 403×3, 410×3, 401`; CU-09 `200×4, 403, 403, 404, 401`.
2. **Datos de prueba:** "PR-09" la precargó CU-08 directamente en "acta en trámite", sin registros de horas, así que muestra 0 horas aprobadas. CU-10 muestra fielmente lo que hay en el repositorio; con datos reales, una práctica llega a "acta en trámite" solo después de completar sus horas (CU-05) y su evaluación (CU-06).

## Anexo: script de ejecución

```python
"""Ejecuta los escenarios de specs/010 contra la composicion de src/main.py."""
import sys
from datetime import datetime, timedelta
sys.path.insert(0, sys.argv[1])
from main import construir


def app():
    a = construir()
    return a, a["controlador"], a["repositorio"], a["bitacora"]


print("== ESC-B")
a, c, r, b = app()
print(" HTTP", *c.consultar_estado("tok-E-1008", "PR-08"))
print(" bitacora:", b.listar())

print("== ESC-EC")
a, c, r, b = app()
print(" HTTP", *c.consultar_estado("tok-E-1010", "PR-10"))

print("== ESC-AC")
a, c, r, b = app()
print(" HTTP", *c.consultar_estado("tok-E-1009", "PR-09"))

print("== ESC-TO")
a, c, r, b = app()
estado, cuerpo = c.consultar_estado("tok-E-1010")
print(" HTTP", estado, "practicas:", [p["id_practica"] for p in cuerpo["practicas"]])

print("== ESC-AJ")
a, c, r, b = app()
print(" HTTP", *c.consultar_estado("tok-E-1010", "PR-08"))
print(" bitacora:", b.listar())

print("== ESC-SR")
a, c, r, b = app()
print(" HTTP", *c.consultar_estado("tok-T-500", "PR-10"))
print(" bitacora:", b.listar())

print("== ESC-PN")
a, c, r, b = app()
print(" HTTP", *c.consultar_estado("tok-E-1010", "PR-99"))

print("== ESC-TV")
a, c, r, b = app()
a["proveedor"].emitir("tok-E-vencido", "E-1010", "Estudiante", datetime.now() - timedelta(minutes=16))
print(" HTTP", *c.consultar_estado("tok-E-vencido"))
```
