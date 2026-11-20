# Validación: 011 Generar reportes de prácticas

Fecha: 2026-11-20. Código validado: `src/` en el commit `8a3175a` (011 T-06). Implementado por Claude sin obreros.

Método: cada escenario se ejecutó contra la composición real de `src/main.py` (`construir()`), con una aplicación nueva por escenario. ESC-CA usa además `src/worker.py` (`construir_worker`). Los valores esperados se cuentan directamente en el repositorio, sin pasar por el caso de uso. El script está en el Anexo. Se ejecuta con `python -B validar_cu11.py <ruta>/src`.

## Validación funcional

| Escenario | Resultado | Evidencia |
|-----------|-----------|-----------|
| ESC-B Reporte general | Cumple | `HTTP 200 {'total_practicas': 10, 'por_estado': {'sin tutor': 2, 'en curso': 5, 'horas completas': 1, 'evaluada': 1, 'acta en trámite': 1, 'cerrada': 0}, 'por_empresa': {'EMP-ACME': 10}, 'por_tutor': {'T-300': 3, 'T-400': 3, 'T-500': 2, 'sin tutor': 2}, 'actas_por_estado': {'sin acta': 9, 'en generación': 0, 'generada': 1, 'aprobada': 0, 'con error': 0}, 'horas_aprobadas': 220, …}`. Esperado según el repositorio: 10 prácticas y 220 horas. Cada grupo suma 10. Están los 6 estados de la práctica y "sin acta" más los 4 del acta. Bitácora `[]`. Código: `src/aplicacion/seguimiento/generar_reporte.py` |
| ESC-CA Refleja los cambios | Cumple | Después de solicitar el acta de PR-08 y procesarla con el Worker: `por_estado[evaluada]` pasa de 1 a 0, `por_estado[acta en trámite]` de 1 a 2, `actas_por_estado[generada]` de 1 a 2 y `actas_por_estado[sin acta]` de 9 a 8 |
| ESC-EM Filtro por empresa sin prácticas | Cumple | `HTTP 200 {'id_empresa': 'EMP-SIN', 'total_practicas': 0, …}`, con todos los conteos en 0 y `por_empresa` y `por_tutor` vacíos |
| ESC-EN Empresa inexistente | Cumple | `HTTP 404 {'codigo': 'empresa_no_encontrada', 'mensaje': 'empresa no encontrada', …}` |
| ESC-SR Sin rol Coordinador (T-500) | Cumple | `HTTP 403`. Bitácora `{'usuario': 'T-500', 'rol': 'Tutor', 'recurso': 'reportes', 'accion': 'generar reporte', 'hora': …}` |
| ESC-TV Token de hace 16 minutos | Cumple | `HTTP 401 {'codigo': 'no_autenticado', …}` |

## Validación arquitectónica

- **Regla de dependencia: cumple.** `dominio/` no importa las otras capas y `aplicacion/` no importa `infraestructura/`.
- **Vista de usos: cumple.** `GenerarReporte` (Seguimiento) usa en solo lectura `ResumirHorasPractica` (Horas) y `ConsultarActaPractica` (Actas); no hay ciclos.
- **ADR:**
  - ADR-004: rol Coordinador en el caso de uso.
  - ADR-006: solo se audita el rechazo.
  - ADR-007: 403 y 404 unificados.
  - No se agregó ninguna librería: el reporte es JSON.
- **Convenciones de AGENTS.md: cumplen.** Una clase por archivo, sin `__init__.py`, sin BOM, DTO `SolicitudReporte` y `ReportePracticas`.

### Observaciones

1. **CU-01 a CU-10 no se rompieron.** Los scripts de los Anexos dan los mismos códigos: CU-01 `201, 409, 409, 201, 409, 409, 201, 404, 403, 401, [201, 201]`; CU-02 `201×3, 404, 400×5, 403, 401`; CU-03 `200×9, 404, 403, 401`; CU-04 `201, 201, 422×8, 404, 403, 403, 401, {201: 300}`; CU-05 `200×4, 422×3, 404, 403, 403, 401`; CU-06 `201, 200, 201, 409, 403, 401, 410, 200, 201, 410×3, 422×4`; CU-07 `202×3, 403, 401, 202` con 500 de 500 actas; CU-08 `201×4, 409×3, 404, 403×3, 410×3, 401`; CU-09 `200×4, 403, 403, 404, 401`; CU-10 `200×4, 403, 403, 404, 401`.
2. **Rendimiento:** el reporte recorre todas las prácticas y consulta horas y acta por cada una. Con las 500 prácticas al año de la visión basta; con PostgreSQL convendría calcularlo con consultas agregadas en el adaptador.

## Anexo: script de ejecución

```python
"""Ejecuta los escenarios de specs/011 contra las composiciones de src/main.py y src/worker.py."""
import sys
from datetime import datetime, timedelta
sys.path.insert(0, sys.argv[1])
from main import construir
from worker import construir_worker
from dominio.empresa import Empresa
from dominio.estado_registro_horas import EstadoRegistroHoras


def app():
    a = construir()
    return a, a["controlador"], a["repositorio"], a["bitacora"]


def esperado(r):
    """Cuenta directamente en el repositorio, sin pasar por el caso de uso."""
    practicas = r.listar_practicas()
    horas = sum(x.horas for x in r.listar_registros_horas() if x.estado == EstadoRegistroHoras.APROBADO)
    return len(practicas), horas


print("== ESC-B")
a, c, r, b = app()
estado, rep = c.generar_reporte("tok-C-01")
total, horas = esperado(r)
print(" HTTP", estado, rep)
print(" esperado: total", total, "| horas aprobadas", horas)
print(" sumas: por_estado", sum(rep["por_estado"].values()), "| por_empresa", sum(rep["por_empresa"].values()),
      "| por_tutor", sum(rep["por_tutor"].values()), "| actas_por_estado", sum(rep["actas_por_estado"].values()))
print(" claves por_estado:", list(rep["por_estado"]), "| claves actas:", list(rep["actas_por_estado"]))
print(" bitacora:", b.listar())

print("== ESC-CA")
a, c, r, b = app()
antes = c.generar_reporte("tok-C-01")[1]
c.solicitar_actas("tok-C-01", {"ids_practicas": ["PR-08"]})
w = construir_worker(r, b, a["notificador"], a["cola_actas"], a["almacen_actas"])
w.procesar(datetime.now() + timedelta(seconds=1))
despues = c.generar_reporte("tok-C-01")[1]
for clave, grupo in (("evaluada", "por_estado"), ("acta en trámite", "por_estado"), ("generada", "actas_por_estado"), ("sin acta", "actas_por_estado")):
    print(f" {grupo}[{clave}]: {antes[grupo][clave]} -> {despues[grupo][clave]}")

print("== ESC-EM")
a, c, r, b = app()
r.agregar_empresa(Empresa("EMP-SIN", "Empresa sin prácticas"))
print(" HTTP", *c.generar_reporte("tok-C-01", "EMP-SIN"))

print("== ESC-EN")
a, c, r, b = app()
print(" HTTP", *c.generar_reporte("tok-C-01", "EMP-99"))

print("== ESC-SR")
a, c, r, b = app()
print(" HTTP", *c.generar_reporte("tok-T-500"))
print(" bitacora:", b.listar())

print("== ESC-TV")
a, c, r, b = app()
a["proveedor"].emitir("tok-C-vencido", "C-01", "CoordinadorPracticas", datetime.now() - timedelta(minutes=16))
print(" HTTP", *c.generar_reporte("tok-C-vencido"))
```
