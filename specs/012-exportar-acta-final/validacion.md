# Validación: 012 Exportar el acta final

Fecha: 2026-11-20. Código validado: `src/` en el commit `8927328` (012 T-06). Implementado por Claude sin obreros.

Método: cada escenario se ejecutó contra la composición real de `src/main.py` (`construir()`), con una aplicación nueva por escenario. ESC-B usa además `src/worker.py` para generar un acta real con ReportLab (ADR-011). Las actas "AC-11" y "AC-12" se agregan como datos. El script está en el Anexo. Se ejecuta con `python -B validar_cu12.py <ruta>/src`.

## Validación funcional

| Escenario | Resultado | Evidencia |
|-----------|-----------|-----------|
| ESC-B El Coordinador exporta el acta del Worker | Cumple | Acta `AC-47f316a2` "generada" por el Worker. `HTTP 200 {'nombre_archivo': 'acta-AC-47f316a2.pdf', 'tipo_contenido': 'application/pdf', 'bytes': 2593, 'inicio': b'%PDF-1.3', 'fin': b'%%EOF'}`. El contenido es igual al guardado por el Worker: `True`. Bitácora nueva `[]`. Código: `src/aplicacion/actas/exportar_acta.py` |
| ESC-ES El Estudiante titular (E-1009) | Cumple | `HTTP 200 {'nombre_archivo': 'acta-AC-09.pdf', 'tipo_contenido': 'application/pdf', …}`. Tras el ajuste T-08: `'bytes': 604, 'inicio': b'%PDF-1.4', 'fin': b'%%EOF'`; el archivo abre como PDF de una página ("Acta final AC-09 (precargada)") |
| ESC-AP Acta aprobada | Cumple | Después de las tres aprobaciones de CU-08, AC-09 está `aprobada` y la exportación da `HTTP 200` con `acta-AC-09.pdf` |
| ESC-SP acta en generación | Cumple | `HTTP 409 {'codigo': 'acta_no_exportable', 'mensaje': 'exportación no permitida', …, 'motivo': 'el acta no tiene PDF generado'}` |
| ESC-SP acta con error | Cumple | `HTTP 409 … 'motivo': 'el acta no tiene PDF generado'` |
| ESC-AN Acta inexistente | Cumple | `HTTP 404 {'codigo': 'acta_no_encontrada', …}` |
| ESC-AJ EAC-04, estudiante ajeno (E-1010) | Cumple | `HTTP 403`. Bitácora `{'usuario': 'E-1010', 'rol': 'Estudiante', 'recurso': 'acta:AC-09', 'accion': 'exportar acta', 'hora': …}` |
| ESC-SR Tutor (no es actor de CU-12) | Cumple | `HTTP 403`. Bitácora `{'usuario': 'T-400', 'rol': 'Tutor', 'recurso': 'acta:AC-09', 'accion': 'exportar acta', 'hora': …}` |
| ESC-AL Archivo inexistente en el repositorio | Cumple | `HTTP 503 {'codigo': 'almacen_no_disponible', 'mensaje': 'repositorio de actas no disponible', …}`. Código: `src/infraestructura/almacen_actas_memoria.py` (`leer`), `controlador_rest.py` (`AlmacenNoDisponible: 503`) |
| ESC-TV Token de hace 16 minutos | Cumple | `HTTP 401 {'codigo': 'no_autenticado', …}` |

## Validación arquitectónica

- **Regla de dependencia: cumple.** `dominio/` no importa las otras capas y `aplicacion/` no importa `infraestructura/`.
- **ADR:**
  - ADR-001 y ADR-011: `ExportarActa` solo recibe `AlmacenActas` y no el `ComponedorActa`, así que la API no compone el PDF.
  - ADR-003: lee por la ruta guardada en el acta.
  - ADR-004: Coordinador o Estudiante titular, verificado en el caso de uso.
  - ADR-006: se auditan solo los rechazos.
  - ADR-007: 409 con motivo, 404 y 503 unificados.
- **Convenciones de AGENTS.md: cumplen.** Una clase por archivo, sin `__init__.py`, sin BOM, DTO en la entrada y la salida.

### Observaciones

1. **CU-01 a CU-11 no se rompieron.** Los scripts de los Anexos dan los mismos códigos: CU-01 `201, 409, 409, 201, 409, 409, 201, 404, 403, 401, [201, 201]`; CU-02 `201×3, 404, 400×5, 403, 401`; CU-03 `200×9, 404, 403, 401`; CU-04 `201, 201, 422×8, 404, 403, 403, 401, {201: 300}`; CU-05 `200×4, 422×3, 404, 403, 403, 401`; CU-06 `201, 200, 201, 409, 403, 401, 410, 200, 201, 410×3, 422×4`; CU-07 `202×3, 403, 401, 202` con 500 de 500 actas; CU-08 `201×4, 409×3, 404, 403×3, 410×3, 401`; CU-09 `200×4, 403, 403, 404, 401`; CU-10 `200×4, 403, 403, 404, 401`; CU-11 `200, 200, 404, 403, 401`.
2. **Contenido de AC-09 (corregido en T-08 y T-09):** la precarga de "AC-09" guardaba 30 bytes de texto (`%PDF-simulado…`). Ahora `src/main.py` (`_pdf_de_prueba`) guarda un PDF mínimo válido de 604 bytes; se abrió con un lector de PDF y su tabla xref apunta a sus 5 objetos. Es un dato precargado del Repositorio de actas, no la composición del acta: esa la sigue haciendo solo el Worker con ReportLab (ADR-001, ADR-011).
3. **Transporte:** el controlador devuelve los bytes en el cuerpo. Con un servidor HTTP real se enviarían con `Content-Type: application/pdf` y `Content-Disposition` con el nombre de archivo.

## Anexo: script de ejecución

```python
"""Ejecuta los escenarios de specs/012 contra las composiciones de src/main.py y src/worker.py."""
import sys
from datetime import datetime, timedelta
sys.path.insert(0, sys.argv[1])
from main import construir
from worker import construir_worker
from dominio.acta_final import ActaFinal
from dominio.estado_acta import EstadoActa


def app():
    a = construir()
    return a, a["controlador"], a["repositorio"], a["bitacora"]


def mostrar(respuesta):
    estado, cuerpo = respuesta
    if estado == 200:
        pdf = cuerpo["contenido"]
        return estado, {"nombre_archivo": cuerpo["nombre_archivo"], "tipo_contenido": cuerpo["tipo_contenido"],
                        "bytes": len(pdf), "inicio": pdf[:8], "fin": pdf.rstrip()[-5:]}
    return estado, cuerpo


print("== ESC-B")
a, c, r, b = app()
c.solicitar_actas("tok-C-01", {"ids_practicas": ["PR-08"]})
construir_worker(r, b, a["notificador"], a["cola_actas"], a["almacen_actas"]).procesar(datetime.now() + timedelta(seconds=1))
acta = next(x for x in r.listar_actas() if x.id_practica == "PR-08")
antes = len(b.listar())
print(" acta del Worker:", acta.id, str(acta.estado))
print(" HTTP", *mostrar(c.exportar_acta("tok-C-01", acta.id)))
print(" igual al guardado por el Worker:", c.exportar_acta("tok-C-01", acta.id)[1]["contenido"] == a["almacen_actas"].leer(acta.ruta_pdf),
      "| bitacora nueva:", b.listar()[antes:])

print("== ESC-ES")
a, c, r, b = app()
print(" HTTP", *mostrar(c.exportar_acta("tok-E-1009", "AC-09")))

print("== ESC-AP")
a, c, r, b = app()
c.aprobar_acta("tok-T-400", "AC-09")
c.emitir_enlace_aprobacion("tok-C-01", "AC-09")
e = next(x for x in r.listar_enlaces() if x.accion == "aprobar acta" and not x.usado)
c.aprobar_acta_con_enlace(e.token)
c.aprobar_acta("tok-C-01", "AC-09")
print(" estado AC-09:", r.obtener_acta("AC-09").estado)
print(" HTTP", *mostrar(c.exportar_acta("tok-C-01", "AC-09")))

for est in (EstadoActa.EN_GENERACION, EstadoActa.CON_ERROR):
    print(f"== ESC-SP ({est})")
    a, c, r, b = app()
    r.guardar_acta(ActaFinal("AC-11", "PR-09", datetime.now(), est))
    print(" HTTP", *c.exportar_acta("tok-C-01", "AC-11"))

print("== ESC-AN")
a, c, r, b = app()
print(" HTTP", *c.exportar_acta("tok-C-01", "AC-99"))

print("== ESC-AJ")
a, c, r, b = app()
print(" HTTP", *c.exportar_acta("tok-E-1010", "AC-09"))
print(" bitacora:", b.listar())

print("== ESC-SR")
a, c, r, b = app()
print(" HTTP", *c.exportar_acta("tok-T-400", "AC-09"))
print(" bitacora:", b.listar())

print("== ESC-AL")
a, c, r, b = app()
r.guardar_acta(ActaFinal("AC-12", "PR-09", datetime.now(), EstadoActa.GENERADA, "actas/no-existe.pdf"))
print(" HTTP", *c.exportar_acta("tok-C-01", "AC-12"))

print("== ESC-TV")
a, c, r, b = app()
a["proveedor"].emitir("tok-C-vencido", "C-01", "CoordinadorPracticas", datetime.now() - timedelta(minutes=16))
print(" HTTP", *c.exportar_acta("tok-C-vencido", "AC-09"))
```
