# Validación: 008 Aprobar el acta final

Fecha: 2026-11-20. Código validado: `src/` en el commit `a74a638` (008 T-14).

Método: cada escenario se ejecutó contra la composición real de `src/main.py` (`construir()`), con una aplicación nueva por escenario y los datos de los Antecedentes de [spec.md](spec.md):
- Practica "PR-09" "acta en trámite" con el Tutor "T-400";
- ActaFinal "AC-09" "generada", con su PDF en el almacén;
- RepresentanteEmpresa "R-01";
- tokens `tok-T-400`, `tok-C-01`, `tok-T-300` y `tok-E-1009`.

Las actas "AC-10" de ESC-NG y los enlaces de "evaluar" o vencidos de ESC-EN se agregan como datos. El script está en el Anexo. Se ejecuta con `python -B validar_cu08.py <ruta>/src`.

## Validación funcional

| Escenario | Resultado | Evidencia |
|-----------|-----------|-----------|
| ESC-B1 Aprueba el Tutor asignado | Cumple | `HTTP 201 {'id_acta': 'AC-09', 'rol': 'Tutor', 'aprobaciones': 1, 'estado_acta': 'generada', 'estado_practica': 'acta en trámite', 'mensaje': 'aprobación registrada'}`. Aprobaciones `[('Tutor', 'T-400')]`. Bitácora `('T-400', 'Tutor', 'acta:AC-09', 'aprobar acta')`. Código: `src/aplicacion/actas/aprobar_acta.py:38-55`, `:84-90` |
| ESC-B2 Enlace y aprobación del Representante | Cumple | Emitir: `HTTP 201 {… 'mensaje': 'enlace de aprobación enviado'}`; enlace `('PR-09', 'aprobar acta', False)`, vence en 7 días; correo a `['representante@acme.example']` con `/aprobaciones-acta/<token>`. Aprobar con el enlace: `HTTP 201 {… 'rol': 'RepresentanteEmpresa', 'aprobaciones': 1, …}`; aprobaciones `[('RepresentanteEmpresa', 'R-01')]`; enlace usado `True`. Bitácora de R-01: `('enlace', 'usar enlace de aprobación')`, `('acta', 'aprobar acta')`. Código: `src/aplicacion/actas/emitir_enlace_aprobacion.py:40-85`, `aprobar_acta.py:57-75` |
| ESC-B3 La tercera aprobación cierra | Cumple | `HTTP 201 {… 'rol': 'CoordinadorPracticas', 'aprobaciones': 3, 'estado_acta': 'aprobada', 'estado_practica': 'cerrada', …}`. Aprobaciones de Tutor, RepresentanteEmpresa y CoordinadorPracticas; PR-09 `cerrada`. Bitácora nueva: `aprobar acta`, `cambiar estado de generada a aprobada`, `cambiar estado de acta en trámite a cerrada`. Código: `aprobar_acta.py:92-103`, `src/dominio/acta_final.py:34`, `src/dominio/practica.py:43` |
| ESC-DO El mismo rol dos veces | Cumple | `HTTP 409 {'codigo': 'aprobacion_no_permitida', 'mensaje': 'aprobación no permitida', …, 'motivo': 'el rol Tutor ya aprobó el acta'}`. Sigue 1 aprobación. Código: `aprobar_acta.py:81-82` |
| ESC-NG acta en generación | Cumple | `HTTP 409 … 'motivo': 'el acta no está generada'`; aprobaciones de AC-10 `[]`. Código: `aprobar_acta.py:79-80` |
| ESC-NG acta con error | Cumple | `HTTP 409 … 'motivo': 'el acta no está generada'`; aprobaciones de AC-10 `[]` |
| ESC-AN Acta inexistente | Cumple | `HTTP 404 {'codigo': 'acta_no_encontrada', 'mensaje': 'acta no encontrada', …}` |
| ESC-AJ EAC-04 tutor no asignado (T-300) | Cumple | `HTTP 403 {'codigo': 'acceso_denegado', …}`; aprobaciones `[]`. Bitácora `{'usuario': 'T-300', 'rol': 'Tutor', 'recurso': 'acta:AC-09', 'accion': 'aprobar acta', 'hora': …}`, con usuario, recurso y hora (medida de EAC-04). Código: `aprobar_acta.py:47-52` |
| ESC-ES Estudiante titular | Cumple | `HTTP 403`; aprobaciones `[]`. Bitácora `{'usuario': 'E-1009', 'rol': 'Estudiante', 'recurso': 'acta:AC-09', 'accion': 'aprobar acta', …}` |
| ESC-SR Enlace pedido sin rol Coordinador | Cumple | `HTTP 403`; enlaces `[]`. Código: `emitir_enlace_aprobacion.py:44-48` |
| ESC-EN enlace de "evaluar" | Cumple | `HTTP 410 {… 'motivo': 'enlace inválido'}`; 0 aprobaciones nuevas; bitácora `('R-01', 'usar enlace rechazado: enlace inválido')`. Código: `src/infraestructura/validador_enlace.py` (reutilizado de CU-06), `src/dominio/enlace_acceso.py:24-32` |
| ESC-EN enlace usado | Cumple | `HTTP 410 {… 'motivo': 'enlace usado'}`; 0 aprobaciones nuevas; bitácora `('R-01', 'usar enlace rechazado: enlace usado')` |
| ESC-EN enlace vencido | Cumple | `HTTP 410 {… 'motivo': 'enlace vencido'}`; 0 aprobaciones nuevas; bitácora `('R-01', 'usar enlace rechazado: enlace vencido')` |
| ESC-TV Token de hace 16 minutos | Cumple | `HTTP 401 {'codigo': 'no_autenticado', …}`; aprobaciones `[]` |

## Validación arquitectónica

- **Regla de dependencia: cumple.** `src/dominio/` no importa `aplicacion` ni `infraestructura`, y `src/aplicacion/` no importa `infraestructura`.
- **Vista de usos sin ciclos: cumple.** El Módulo Actas usa el DTO `EnlaceEmitido` del Módulo Evaluación (permitido: Actas usa Evaluación), y Evaluación no usa Actas.
- **Cada ADR del plan se ve en el código:**
  - ADR-002: los casos de uso están en el Módulo Actas.
  - ADR-004: rol y titularidad del tutor en el caso de uso (`aprobar_acta.py:47`).
  - ADR-005: el enlace "aprobar acta" lo valida el mismo `ValidadorEnlace`, y es de un solo uso (`aprobar_acta.py:66`), con vencimiento y reemisión (`emitir_enlace_aprobacion.py:61`).
  - ADR-006: cada `Aprobacion` guarda rol, usuario y fecha, y se auditan las aprobaciones, los cambios de estado y los rechazos.
  - ADR-007: 404 y 409 con motivo (`controlador_rest.py:62-63`).
- **Convenciones de AGENTS.md: cumplen.** Una clase por archivo (99 archivos en `src/`), cero `__init__.py`, ningún BOM y LF en el índice. DTO en la entrada y la salida. Nombres del glosario (`Aprobacion`, `ActaFinal`, `EnlaceAcceso`). Solo librería estándar.

### Observaciones

1. **CU-01 a CU-07 no se rompieron.** Los scripts de los Anexos dan los mismos códigos: CU-01 `201, 409, 409, 201, 409, 409, 201, 404, 403, 401, [201, 201]`; CU-02 `201×3, 404, 400×5, 403, 401`; CU-03 `200×9, 404, 403, 401`; CU-04 `201, 201, 422×8, 404, 403, 403, 401, {201: 300}`; CU-05 `200×4, 422×3, 404, 403, 403, 401`; CU-06 `201, 200, 201, 409, 403, 401, 410, 200, 201, 410×3, 422×4`; CU-07 `202, 202, 202, 403, 401, 202`, con 500 de 500 actas generadas o en errores. `python src/main.py` y `python src/worker.py` se ejecutan sin errores.
2. **Tipo en el controlador:** `_cuerpo_aprobacion(resultado: object)` anota el parámetro como `object` en lugar de `AprobacionRegistrada`. Funciona, pero conviene ajustarlo al tocar el controlador en el próximo caso de uso.
3. **Proceso:** en T-14, la auditoría marcó una diferencia que era un error del contenido esperado (un `\n` escrito como salto de línea real). El archivo del obrero era el correcto y se verificó con `construir()` antes del commit.

## Anexo: script de ejecución

```python
"""Ejecuta los escenarios de specs/008 contra la composicion de src/main.py."""
import sys
from datetime import datetime, timedelta
sys.path.insert(0, sys.argv[1])
from main import construir
from dominio.acta_final import ActaFinal
from dominio.enlace_acceso import EnlaceAcceso
from dominio.estado_acta import EstadoActa


def app():
    a = construir()
    return a, a["controlador"], a["repositorio"], a["bitacora"], a["notificador"]


def estado(r, id_acta="AC-09"):
    acta = r.obtener_acta(id_acta)
    return f"{id_acta}={acta.estado} aprobaciones={[(x.rol, x.usuario) for x in r.listar_aprobaciones(id_acta)]} PR-09={r.obtener_practica('PR-09').estado}"


def enlace_aprobacion(c, r):
    c.emitir_enlace_aprobacion("tok-C-01", "AC-09")
    return next(e for e in r.listar_enlaces() if e.accion == "aprobar acta" and not e.usado)


print("== ESC-B1")
a, c, r, b, n = app()
print(" HTTP", *c.aprobar_acta("tok-T-400", "AC-09"))
print(" ", estado(r))
print(" bitacora:", [(x["usuario"], x["rol"], x["recurso"], x["accion"]) for x in b.listar()])

print("== ESC-B2")
a, c, r, b, n = app()
print(" HTTP", *c.emitir_enlace_aprobacion("tok-C-01", "AC-09"))
e = next(x for x in r.listar_enlaces() if x.accion == "aprobar acta")
print(" enlace:", (e.id_practica, e.accion, e.usado), "vence en:", e.vence.date() - datetime.now().date())
print(" correo:", [(x["destinatarios"], x["mensaje"].replace(e.token, "<token>")) for x in n.listar_enviados()])
print(" HTTP", *c.aprobar_acta_con_enlace(e.token))
print(" ", estado(r), "| enlace usado:", r.obtener_enlace_por_token(e.token).usado)
print(" bitacora R-01:", [(x["usuario"], x["recurso"].split(":")[0], x["accion"]) for x in b.listar() if x["usuario"] == "R-01"])

print("== ESC-B3")
a, c, r, b, n = app()
c.aprobar_acta("tok-T-400", "AC-09")
c.aprobar_acta_con_enlace(enlace_aprobacion(c, r).token)
antes = len(b.listar())
print(" HTTP", *c.aprobar_acta("tok-C-01", "AC-09"))
print(" ", estado(r))
print(" bitacora nueva:", [(x["usuario"], x["recurso"], x["accion"]) for x in b.listar()[antes:]])

print("== ESC-DO")
a, c, r, b, n = app()
c.aprobar_acta("tok-T-400", "AC-09")
print(" HTTP", *c.aprobar_acta("tok-T-400", "AC-09"))
print(" ", estado(r))

for est in (EstadoActa.EN_GENERACION, EstadoActa.CON_ERROR):
    print(f"== ESC-NG ({est})")
    a, c, r, b, n = app()
    r.guardar_acta(ActaFinal("AC-10", "PR-09", datetime.now(), est))
    print(" HTTP", *c.aprobar_acta("tok-C-01", "AC-10"))
    print(" aprobaciones AC-10:", r.listar_aprobaciones("AC-10"))

print("== ESC-AN")
a, c, r, b, n = app()
print(" HTTP", *c.aprobar_acta("tok-C-01", "AC-99"))

print("== ESC-AJ")
a, c, r, b, n = app()
print(" HTTP", *c.aprobar_acta("tok-T-300", "AC-09"))
print(" ", estado(r), "| bitacora:", b.listar())

print("== ESC-ES")
a, c, r, b, n = app()
print(" HTTP", *c.aprobar_acta("tok-E-1009", "AC-09"))
print(" ", estado(r), "| bitacora:", b.listar())

print("== ESC-SR")
a, c, r, b, n = app()
print(" HTTP", *c.emitir_enlace_aprobacion("tok-T-400", "AC-09"))
print(" enlaces:", r.listar_enlaces())

for caso in ("evaluar", "usado", "vencido"):
    print(f"== ESC-EN ({caso})")
    a, c, r, b, n = app()
    if caso == "evaluar":
        e = EnlaceAcceso.emitir("EN-ev", "tok-ev", "PR-09", "R-01", "evaluar", datetime.now())
        r.guardar_enlace(e)
    elif caso == "usado":
        e = enlace_aprobacion(c, r)
        c.aprobar_acta_con_enlace(e.token)
    else:
        e = EnlaceAcceso.emitir("EN-viejo", "tok-viejo", "PR-09", "R-01", "aprobar acta", datetime.now() - timedelta(days=8))
        r.guardar_enlace(e)
    previas = len(r.listar_aprobaciones("AC-09"))
    antes = len(b.listar())
    print(" HTTP", *c.aprobar_acta_con_enlace(e.token))
    print(" aprobaciones nuevas:", len(r.listar_aprobaciones("AC-09")) - previas,
          "| bitacora nueva:", [(x["usuario"], x["accion"]) for x in b.listar()[antes:]])

print("== ESC-TV")
a, c, r, b, n = app()
a["proveedor"].emitir("tok-T-vencido", "T-400", "Tutor", datetime.now() - timedelta(minutes=16))
print(" HTTP", *c.aprobar_acta("tok-T-vencido", "AC-09"))
print(" ", estado(r))
```
