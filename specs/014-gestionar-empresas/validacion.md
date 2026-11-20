# Validación: 014 Gestionar empresas aliadas y sus representantes

Fecha: 2026-11-20. Código validado: `src/` en el commit `b9dab68` (014 T-12). Implementado por Claude sin obreros.

Método: cada escenario se ejecutó contra la composición real de `src/main.py` (`construir()`), con una aplicación nueva por escenario y los datos de los Antecedentes de [spec.md](spec.md): Empresa "EMP-ACME" (con la Plaza "PL-01" y prácticas), su representante "R-01" y el Coordinador "C-01" (`tok-C-01`). El script está en el Anexo. Se ejecuta con `python -B validar_cu14.py <ruta>/src`.

## Validación funcional

| Escenario | Resultado | Evidencia |
|-----------|-----------|-----------|
| ESC-B Crear empresa y representante | Cumple | `HTTP 201 {'id': 'EMP-NUEVA', 'razon_social': 'Nueva Ltda.', 'nit': '900123456-7', 'representante': None}`, y luego `HTTP 200` con `'representante': {'id': 'R-34c3ff6c', 'nombre': 'Ana Pérez', 'correo': 'ana@nueva.example'}`. Publicar una Plaza de EMP-NUEVA (CU-02) da `HTTP 201`. Bitácora `[]`. Código: `src/aplicacion/postulaciones/gestionar_empresas.py` (`crear`, `registrar_representante`) |
| ESC-LI Listar | Cumple | `HTTP 200 {'empresas': [{'id': 'EMP-ACME', 'razon_social': 'Acme S.A.S.', 'nit': '900123456-7', 'representante': {'id': 'R-01', …, 'correo': 'representante@acme.example'}}]}` |
| ESC-AC Actualizar | Cumple | `HTTP 200 {'id': 'EMP-ACME', 'razon_social': 'Acme Colombia S.A.S.', 'nit': '800765432-1', …}`. Plazas de EMP-ACME antes y después: `['PL-01']` |
| ESC-CO Correo actualizado (ADR-005) | Cumple | El representante conserva el id `R-01` y queda con el correo `nuevo@acme.example`. El enlace de evaluación de PR-06 que se emite después (`HTTP 201`) se envía a `[['nuevo@acme.example']]` |
| ESC-EL Eliminar sin plazas ni prácticas | Cumple | `HTTP 204 {}`; la empresa y su representante quedan en `None` |
| ESC-EP Eliminar con plazas o prácticas | Cumple | `HTTP 409 {'codigo': 'empresa_no_permitida', 'mensaje': 'empresa no permitida', …, 'motivo': 'la empresa tiene plazas o prácticas'}`; EMP-ACME sigue registrada |
| ESC-YE Id existente | Cumple | `HTTP 409 … 'motivo': 'ya existe empresa EMP-ACME'` |
| ESC-DI razón social vacía | Cumple | `HTTP 400 {'codigo': 'empresa_no_valida', 'mensaje': 'empresa no válida', …, 'motivo': 'la razón social es obligatoria'}`; EMP-X no se crea. Código: `src/dominio/empresa.py` (`motivo_invalidez`) |
| ESC-DI NIT "123" | Cumple | `HTTP 400 … 'motivo': 'el NIT debe tener 9 dígitos, un guion y el dígito de verificación'` |
| ESC-DI nombre vacío | Cumple | `HTTP 400 … 'motivo': 'el nombre del representante es obligatorio'`; el correo de R-01 no cambia. Código: `src/dominio/representante_empresa.py` |
| ESC-DI correo sin arroba | Cumple | `HTTP 400 … 'motivo': 'el correo no es válido'`. Código: `src/dominio/correo.py` (de CU-13) |
| ESC-EN Empresa inexistente | Cumple | `HTTP 404 {'codigo': 'empresa_no_encontrada', …}` |
| ESC-SR Sin rol Coordinador (T-500) | Cumple | `HTTP 403`; EMP-T no se crea. Bitácora `{'usuario': 'T-500', 'rol': 'Tutor', 'recurso': 'empresa:EMP-T', 'accion': 'gestionar empresas', 'hora': …}` |
| ESC-TV Token de hace 16 minutos | Cumple | `HTTP 401 {'codigo': 'no_autenticado', …}` |

## Validación arquitectónica

- **Regla de dependencia: cumple.** `dominio/` solo importa la librería estándar y `dominio/`; `aplicacion/` no importa `infraestructura/`.
- **Vista de desarrollo: cumple.** El caso de uso está en el Módulo Postulaciones (CU-01, CU-02 y CU-14), que solo usa puertos y dominio.
- **ADR:**
  - ADR-004: rol Coordinador en el caso de uso.
  - ADR-005: el correo del representante es el destino de los enlaces nuevos (ESC-CO).
  - ADR-006: se audita solo el rechazo, porque Empresa no tiene cambios de estado auditables.
  - ADR-007: 400 y 409 con motivo, y 404.
- **Convenciones de AGENTS.md: cumplen.** Una clase por archivo, sin `__init__.py`, sin BOM, DTO en la entrada y la salida. `Empresa` agrega `nit` con valor por defecto, así que las precargas anteriores siguen valiendo.

### Observaciones

1. **CU-01 a CU-13 no se rompieron.** Los scripts de los Anexos dan los mismos códigos: CU-01 `201, 409, 409, 201, 409, 409, 201, 404, 403, 401, [201, 201]`; CU-02 `201×3, 404, 400×5, 403, 401`; CU-03 `200×9, 404, 403, 401`; CU-04 `201, 201, 422×8, 404, 403, 403, 401, {201: 300}`; CU-05 `200×4, 422×3, 404, 403, 403, 401`; CU-06 `201, 200, 201, 409, 403, 401, 410, 200, 201, 410×3, 422×4`; CU-07 `202×3, 403, 401, 202` con 500 de 500 actas; CU-08 `201×4, 409×3, 404, 403×3, 410×3, 401`; CU-09 `200×4, 403, 403, 404, 401`; CU-10 `200×4, 403, 403, 404, 401`; CU-11 `200, 200, 404, 403, 401`; CU-12 `200×3, 409, 409, 404, 403, 403, 503, 401`; CU-13 `200×4, 403, 401`.
2. **Eliminar la empresa elimina también su representante**, así ningún enlace nuevo puede ir a una empresa inexistente.

## Anexo: script de ejecución

```python
"""Ejecuta los escenarios de specs/014 contra la composicion de src/main.py."""
import sys
from datetime import datetime, timedelta
sys.path.insert(0, sys.argv[1])
from main import construir


def app():
    a = construir()
    return a, a["controlador"], a["repositorio"], a["bitacora"], a["notificador"]


NUEVA = {"id": "EMP-NUEVA", "razon_social": "Nueva Ltda.", "nit": "900123456-7"}

print("== ESC-B")
a, c, r, b, n = app()
print(" HTTP", *c.crear_empresa("tok-C-01", NUEVA))
print(" HTTP", *c.registrar_representante("tok-C-01", "EMP-NUEVA", {"nombre": "Ana Pérez", "correo": "ana@nueva.example"}))
print(" empresa:", r.obtener_empresa("EMP-NUEVA"), "| representante:", r.obtener_representante_de_empresa("EMP-NUEVA"))
print(" publicar plaza (CU-02): HTTP", c.publicar_plaza("tok-C-01", {"id_empresa": "EMP-NUEVA", "cargo": "Analista", "cupos": 1, "periodo": "2026-2"})[0])
print(" bitacora:", b.listar())

print("== ESC-LI")
a, c, r, b, n = app()
print(" HTTP", *c.listar_empresas("tok-C-01"))

print("== ESC-AC")
a, c, r, b, n = app()
plazas_antes = [p.id for p in r.listar_plazas() if p.id_empresa == "EMP-ACME"]
print(" HTTP", *c.actualizar_empresa("tok-C-01", "EMP-ACME", {"razon_social": "Acme Colombia S.A.S.", "nit": "800765432-1"}))
print(" plazas de EMP-ACME antes y despues:", plazas_antes, [p.id for p in r.listar_plazas() if p.id_empresa == "EMP-ACME"])

print("== ESC-CO")
a, c, r, b, n = app()
print(" HTTP", *c.registrar_representante("tok-C-01", "EMP-ACME", {"nombre": "Representante de Acme", "correo": "nuevo@acme.example"}))
print(" HTTP enlace PR-06:", c.emitir_enlace_evaluacion("tok-C-01", "PR-06")[0],
      "| correo enviado a:", [x["destinatarios"] for x in n.listar_enviados()])

print("== ESC-EL")
a, c, r, b, n = app()
c.crear_empresa("tok-C-01", NUEVA)
c.registrar_representante("tok-C-01", "EMP-NUEVA", {"nombre": "Ana", "correo": "ana@nueva.example"})
print(" HTTP", *c.eliminar_empresa("tok-C-01", "EMP-NUEVA"))
print(" empresa:", r.obtener_empresa("EMP-NUEVA"), "| representante:", r.obtener_representante_de_empresa("EMP-NUEVA"))

print("== ESC-EP")
a, c, r, b, n = app()
print(" HTTP", *c.eliminar_empresa("tok-C-01", "EMP-ACME"))
print(" sigue:", r.obtener_empresa("EMP-ACME") is not None)

print("== ESC-YE")
a, c, r, b, n = app()
print(" HTTP", *c.crear_empresa("tok-C-01", {"id": "EMP-ACME", "razon_social": "Otra", "nit": "900123456-7"}))

for nombre, llamada in [
    ("razon social vacia", lambda c: c.crear_empresa("tok-C-01", {"id": "EMP-X", "razon_social": "", "nit": "900123456-7"})),
    ("NIT 123", lambda c: c.crear_empresa("tok-C-01", {"id": "EMP-X", "razon_social": "X", "nit": "123"})),
    ("nombre vacio", lambda c: c.registrar_representante("tok-C-01", "EMP-ACME", {"nombre": "", "correo": "a@b.co"})),
    ("correo sin arroba", lambda c: c.registrar_representante("tok-C-01", "EMP-ACME", {"nombre": "Ana", "correo": "sin-arroba"})),
]:
    print(f"== ESC-DI ({nombre})")
    a, c, r, b, n = app()
    print(" HTTP", *llamada(c))
    print(" EMP-X:", r.obtener_empresa("EMP-X"), "| representante EMP-ACME:", r.obtener_representante_de_empresa("EMP-ACME").correo)

print("== ESC-EN")
a, c, r, b, n = app()
print(" HTTP", *c.actualizar_empresa("tok-C-01", "EMP-99", {"razon_social": "X", "nit": "900123456-7"}))

print("== ESC-SR")
a, c, r, b, n = app()
print(" HTTP", *c.crear_empresa("tok-T-500", {"id": "EMP-T", "razon_social": "T", "nit": "900123456-7"}))
print(" EMP-T:", r.obtener_empresa("EMP-T"), "| bitacora:", b.listar())

print("== ESC-TV")
a, c, r, b, n = app()
a["proveedor"].emitir("tok-C-vencido", "C-01", "CoordinadorPracticas", datetime.now() - timedelta(minutes=16))
print(" HTTP", *c.listar_empresas("tok-C-vencido"))
```
