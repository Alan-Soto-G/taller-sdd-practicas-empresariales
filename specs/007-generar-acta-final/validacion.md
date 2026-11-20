# Validación: 007 Generar el acta final

Fecha: 2026-11-20. Código validado: `src/` en el commit `273e7c6` (007 T-23) y revalidado en `e8092a3` (007 T-31), después del ajuste de ADR-011: el PDF lo compone ReportLab 5.1.0 detrás del puerto `ComponedorActa`.

Método: cada escenario se ejecutó contra las dos composiciones reales: la de la API, `src/main.py` (`construir()`), y la del Worker de actas, `src/worker.py` (`construir_worker(...)`), que en esta etapa reciben los mismos adaptadores en memoria. Se usó una aplicación nueva por escenario y los datos de los Antecedentes de [spec.md](spec.md): Practica "PR-08" "evaluada" con 160 horas aprobadas y su Evaluacion, Coordinador "C-01" con correo y `tok-C-01`, y Tutor "T-400" (`tok-T-400`).

El Worker recibe un reloj simulado. Ese reloj se pone al día después de cada solicitud de la API y se avanza a mano para comprobar las esperas de 1 y 2 min. Las fallas se simulan con `AlmacenActasMemoria.fallas_pendientes`. El script está en el Anexo. Se ejecuta con `python -B validar_cu07.py <ruta>/src`.

## Validación funcional

| Escenario | Resultado | Evidencia |
|-----------|-----------|-----------|
| ESC-B1 La API solo encola | Cumple | `HTTP 202 {'resultados': [{'id_practica': 'PR-08', 'id_acta': 'AC-b6b5727c', 'resultado': 'en generación'}], 'mensaje': 'actas en generación; se le notificará'}`. Actas `[('PR-08', 'en generación', None)]`; PR-08 `acta en trámite`. Cola actas `[('PR-08', 1)]`. PDF en el almacén: `[]`, es decir que la API no compone el acta. Bitácora: `('C-01', 'acta', 'crear con estado en generación')`, `('C-01', 'practica', 'cambiar estado de evaluada a acta en trámite')`. Código: `src/aplicacion/actas/solicitar_actas.py:62-76` |
| ESC-B2 El Worker genera el acta | Cumple | Procesadas: 1. PDF `actas/AC-2f53330b.pdf` de 2593 bytes, generado por ReportLab: cabecera `%PDF-1.3` y fin `%%EOF`. Contiene el id del acta, `Horas aprobadas: 160 de 160`, `plantilla-acta-v1` y `Responsabilidad: 5` (las páginas van sin comprimir). Una copia se abrió como PDF (`acta_cu07.pdf` en el directorio de ejecución). Intentos `[(1, 'exitoso')]`. Acta `('PR-08', 'generada', 'actas/AC-2f53330b.pdf')`. Correo a `['t400@universidad.edu.co', 'representante@acme.example', 'coordinacion@universidad.edu.co']`. Cola actas `[]`. Bitácora `('worker-actas', 'cambiar estado de en generación a generada')`. Código: `src/aplicacion/actas/generar_acta.py:54-56` (consolida y pide el PDF al puerto), `:73-89` (`_consolidar` → `DatosActa`), `src/infraestructura/componedor_acta_reportlab.py:19-29` |
| ESC-NE Práctica no evaluada (PR-04) | Cumple | `HTTP 202` con `'no solicitada: la práctica no está evaluada'`. Actas `[]`, cola `[]`. Código: `solicitar_actas.py:56-59` |
| ESC-PN Práctica inexistente | Cumple | `HTTP 202` con `'no solicitada: práctica no encontrada'`. Actas `[]`. Código: `solicitar_actas.py:51-54` |
| ESC-SR Sin rol Coordinador (T-400) | Cumple | `HTTP 403 {'codigo': 'acceso_denegado', …}`. Actas `[]`. Bitácora `{'usuario': 'T-400', 'rol': 'Tutor', 'recurso': 'practica:PR-08', 'accion': 'solicitar acta', 'hora': …}`. Código: `solicitar_actas.py:41-46` |
| ESC-TV Token de hace 16 minutos | Cumple | `HTTP 401 {'codigo': 'no_autenticado', …}`. Actas `[]` |
| ESC-R1 Falla una vez | Cumple | Intentos `[(1, 'fallido: repositorio de actas no disponible')]`. Cola actas `[(2, '0:01:00')]`: el intento 2 está disponible 1 min después. A los 59 s el Worker procesa 0; a los 60 s procesa 1. Intentos `[(1, 'fallido: …'), (2, 'exitoso')]`; acta `generada`. Código: `generar_acta.py:50-56`, `src/dominio/intento_generacion.py:6-20`, `src/infraestructura/worker_actas.py:22-24`, `src/infraestructura/cola_actas_memoria.py:28-35` |
| ESC-R3 Falla 3 veces | Cumple | Con esperas de 1 y 2 min, intentos `[(1, 'fallido: …'), (2, 'fallido: …'), (3, 'fallido: …')]`. `errores_actas` `[('PR-08', 3)]`; cola actas `[]`. Acta `('PR-08', 'con error', None)`. Bitácora `('worker-actas', 'cambiar estado de en generación a con error')`. Código: `generar_acta.py:54-58`, `worker_actas.py:25-26` |
| ESC-RC Falla al componer el PDF (ajuste ADR-011) | Cumple | Componedor que falla una vez: intentos `[(1, 'fallido: no se pudo componer el PDF del acta'), (2, 'exitoso')]`; acta `generada`. El adaptador real con datos inválidos lanza `ActaNoComponible: no se pudo componer el PDF del acta`. Código: `generar_acta.py:56` (`except (ActaNoComponible, AlmacenNoDisponible)`), `componedor_acta_reportlab.py:19-24` (traduce cualquier excepción, ADR-007) |
| ESC-CO Falla el correo de aviso | Cumple | Acta `('PR-08', 'generada', …)`; enviados `[]`; pendientes `[['t400@…', 'representante@acme.example', 'coordinacion@…']]`. Código: `generar_acta.py:108-115` |
| ESC-E2 EAC-02, 500 actas con 30 fallas | Cumple | `HTTP 202`, aceptada en 0,006 s (medida: menos de 3 s); 500 resultados "en generación". 500 actas, es decir 0 perdidas. 500 generadas y 0 en `errores_actas`: el 100% termina generada o en errores. Los 500 PDF son válidos (empiezan con `%PDF-`). Cola actas vacía; 30 intentos fallidos registrados. Generadas en 10 min o menos: 500 de 500, el 100% (medida: 95%); el máximo fue 0:01:00 |

## Validación arquitectónica

- **Regla de dependencia: cumple.** `src/dominio/` solo importa la librería estándar y módulos de `dominio`. Ningún archivo de `src/aplicacion/` importa `infraestructura`.
- **Vista de usos sin ciclos: cumple.** El Módulo Actas (`src/aplicacion/actas/`) solo usa puertos y dominio.
- **Cada ADR del plan se ve en el código:**
  - ADR-001: la API solo registra y publica (`solicitar_actas.py:75`); ningún archivo de la API llama al `AlmacenActas` para escribir. `GenerarActa` solo lo compone `src/worker.py:15-24`. Hay 3 intentos con esperas de 1 y 2 min (`intento_generacion.py:6-7`) y la cola `errores_actas` (`cola_actas_memoria.py:37-40`).
  - ADR-002: el Worker de actas tiene su propia composición (`src/worker.py`) y reutiliza `dominio/`, `GenerarActa` y los adaptadores.
  - ADR-003: el PDF va al `AlmacenActas` y el acta guarda solo la ruta (`acta_final.py`, `ruta_pdf`).
  - ADR-004: rol Coordinador en el caso de uso (`solicitar_actas.py:41`).
  - ADR-006: se auditan la creación del acta, el cambio de la Práctica, los cambios del Worker (`generar_acta.py:91-100`) y el acceso rechazado; `IntentoGeneracion` registra cada intento.
  - ADR-007: el almacén traduce su falla a `AlmacenNoDisponible` (`almacen_actas_memoria.py:13-20`) y el adaptador PDF a `ActaNoComponible`; si el correo falla, el acta no se revierte.
  - ADR-011: ReportLab detrás del puerto `ComponedorActa`; las dos fallas cuentan como intento fallido (ESC-RC).
  - ADR-008: la plantilla y las horas requeridas salen de la versión de la regla de la práctica (`generar_acta.py:69`).
- **DT-05 resuelta por ADR-011:** `src/requirements.txt` fija `reportlab==5.1.0`. Solo `src/infraestructura/componedor_acta_reportlab.py` importa `reportlab`; `aplicacion/` usa el puerto `ComponedorActa` (`src/aplicacion/puertos/componedor_acta.py`). Solo `src/worker.py` lo compone: `src/main.py` (la API) no lo recibe (ADR-001). La primera versión (hasta `007 T-24`) usaba un documento simulado.
- **Convenciones de AGENTS.md: cumplen.** Una clase por archivo (`main.py` y `worker.py` solo tienen funciones), cero `__init__.py`, ningún BOM y LF en el índice. DTO en la entrada y la salida. Nombres del glosario (`ActaFinal`, `IntentoGeneracion`, `PublicadorActas`, `AlmacenActas`, mensaje `SolicitudActa`, colas `actas` y `errores_actas`). Solo librería estándar.

### Observaciones

1. **CU-01 a CU-06 no se rompieron.** Los scripts de los Anexos dan los mismos códigos: CU-01 `201, 409, 409, 201, 409, 409, 201, 404, 403, 401, [201, 201]`; CU-02 `201×3, 404, 400×5, 403, 401`; CU-03 `200×9, 404, 403, 401`; CU-04 `201, 201, 422×8, 404, 403, 403, 401, {201: 300}`; CU-05 `200×4, 422×3, 404, 403, 403, 401`; CU-06 `201, 200, 201, 409, 403, 401, 410, 200, 201, 410×3, 422×4`, con la misma huella de `src/` antes y después del escenario EAC-03.
2. **`worker.py` en modo de demostración:** su `main()` importa la composición de la API para compartir los adaptadores en memoria de esta etapa. En producción, el Worker se conecta a PostgreSQL y RabbitMQ con su propia configuración, y `construir_worker` no depende de la API.
3. **Ajuste del script:** desde CU-08, `main.py` precarga el acta "AC-09". El script toma el acta de "PR-08" por su práctica (`acta_pr08`) y no por su posición en la lista, y no muestra "AC-09".
4. **Medida de tiempos de EAC-02:** se toma con la composición en memoria y un reloj simulado. Con 30 fallas, ninguna acta agotó los 3 intentos, porque cada falla consume uno de los 500 primeros intentos. ESC-R3 cubre el paso a `errores_actas`.
5. **Proceso:** en T-12, copilot escribió el archivo pero no terminó. Se cambió el lanzador de obreros para detenerlos en cuanto el archivo tiene el contenido esperado.

## Anexo: script de ejecución

Se ejecuta con `python -B validar_cu07.py <ruta>/src [ruta del PDF de muestra]`.

```python
"""Ejecuta los escenarios de specs/007 contra las composiciones de src/main.py (API) y src/worker.py (Worker de actas)."""
import sys
import time
from datetime import date, datetime, timedelta
sys.path.insert(0, sys.argv[1])
from main import construir
from worker import construir_worker
from dominio.estado_practica import EstadoPractica
from dominio.estudiante import Estudiante
from dominio.evaluacion import Evaluacion
from dominio.practica import Practica


class Reloj:
    def __init__(self):
        self.ahora = datetime.now()

    def __call__(self):
        return self.ahora

    def sincronizar(self):
        """El Worker corre despues de que la API publica: su reloj no puede ir detras."""
        self.ahora = max(self.ahora, datetime.now())

    def avanzar(self, **kw):
        self.ahora += timedelta(**kw)


def app():
    a = construir()
    reloj = Reloj()
    w = construir_worker(a["repositorio"], a["bitacora"], a["notificador"], a["cola_actas"], a["almacen_actas"], reloj)
    global RELOJ
    RELOJ = reloj
    return a, a["controlador"], a["repositorio"], a["bitacora"], a["notificador"], a["cola_actas"], a["almacen_actas"], w, reloj


def actas(r):
    """Actas creadas en el escenario (sin el acta AC-09 que precarga CU-08)."""
    return [(x.id_practica, str(x.estado), x.ruta_pdf) for x in r.listar_actas() if x.id != "AC-09"]


def acta_pr08(r):
    return next(x for x in r.listar_actas() if x.id_practica == "PR-08")


def cola(q):
    return [(s.id_practica, s.intento) for _, s in q.listar_actas()]


RELOJ = None


def solicitar(c, ids, token="tok-C-01"):
    respuesta = c.solicitar_actas(token, {"ids_practicas": ids})
    RELOJ.sincronizar()
    return respuesta


print("== ESC-B1")
a, c, r, b, n, q, al, w, reloj = app()
print(" HTTP", *solicitar(c, ["PR-08"]))
print(" actas:", actas(r), "| PR-08:", r.obtener_practica("PR-08").estado)
print(" cola actas:", cola(q), "| PDF en el almacen (sin el de AC-09):", [x for x in al.listar() if "AC-09" not in x])
print(" bitacora:", [(x["usuario"], x["recurso"].split(":")[0], x["accion"]) for x in b.listar()])

print("== ESC-B2")
a, c, r, b, n, q, al, w, reloj = app()
solicitar(c, ["PR-08"])
print(" procesadas:", w.procesar(reloj()))
acta = acta_pr08(r)
pdf = al.leer(acta.ruta_pdf)
open(sys.argv[2] if len(sys.argv) > 2 else "acta_cu07.pdf", "wb").write(pdf)
print(" PDF:", acta.ruta_pdf, "| bytes:", len(pdf), "| cabecera:", pdf[:8], "| fin:", pdf.rstrip()[-5:])
print(" contiene: id del acta", acta.id.encode() in pdf, "| 'Horas aprobadas: 160 de 160'", b"Horas aprobadas: 160 de 160" in pdf,
      "| 'plantilla-acta-v1'", b"plantilla-acta-v1" in pdf, "| 'Responsabilidad: 5'", b"Responsabilidad: 5" in pdf)
print(" intentos:", [(i.numero, i.resultado) for i in r.listar_intentos(acta.id)])
print(" acta:", actas(r))
print(" correo:", [(x["destinatarios"], x["mensaje"]) for x in n.listar_enviados()])
print(" cola actas:", cola(q), "| bitacora worker:", [(x["usuario"], x["accion"]) for x in b.listar() if x["usuario"] == "worker-actas"])

print("== ESC-NE")
a, c, r, b, n, q, al, w, reloj = app()
print(" HTTP", *solicitar(c, ["PR-04"]))
print(" actas:", actas(r), "cola:", cola(q))

print("== ESC-PN")
a, c, r, b, n, q, al, w, reloj = app()
print(" HTTP", *solicitar(c, ["PR-99"]))
print(" actas:", actas(r))

print("== ESC-SR")
a, c, r, b, n, q, al, w, reloj = app()
print(" HTTP", *solicitar(c, ["PR-08"], token="tok-T-400"))
print(" actas:", actas(r), "bitacora:", b.listar())

print("== ESC-TV")
a, c, r, b, n, q, al, w, reloj = app()
a["proveedor"].emitir("tok-C-vencido", "C-01", "CoordinadorPracticas", datetime.now() - timedelta(minutes=16))
print(" HTTP", *solicitar(c, ["PR-08"], token="tok-C-vencido"))
print(" actas:", actas(r))

print("== ESC-R1")
a, c, r, b, n, q, al, w, reloj = app()
solicitar(c, ["PR-08"])
al.fallas_pendientes = 1
w.procesar(reloj())
acta = acta_pr08(r)
print(" intentos:", [(i.numero, i.resultado) for i in r.listar_intentos(acta.id)])
print(" cola actas:", [(s.intento, str(d - reloj())) for d, s in q.listar_actas()])
reloj.avanzar(seconds=59)
print(" a los 59 s, procesadas:", w.procesar(reloj()))
reloj.avanzar(seconds=1)
print(" a los 60 s, procesadas:", w.procesar(reloj()))
print(" intentos:", [(i.numero, i.resultado) for i in r.listar_intentos(acta.id)], "| acta:", actas(r))

print("== ESC-R3")
a, c, r, b, n, q, al, w, reloj = app()
solicitar(c, ["PR-08"])
al.fallas_pendientes = 3
w.procesar(reloj())
reloj.avanzar(minutes=1)
w.procesar(reloj())
reloj.avanzar(minutes=2)
w.procesar(reloj())
acta = acta_pr08(r)
print(" intentos:", [(i.numero, i.resultado) for i in r.listar_intentos(acta.id)])
print(" errores_actas:", [(s.id_practica, s.intento) for s in q.listar_errores()], "| actas:", cola(q))
print(" acta:", actas(r))
print(" bitacora worker:", [(x["usuario"], x["accion"]) for x in b.listar() if x["usuario"] == "worker-actas"])

print("== ESC-RC")
a, c, r, b, n, q, al, w, reloj = app()
solicitar(c, ["PR-08"])
from aplicacion.errores.acta_no_componible import ActaNoComponible
real = w._generar_acta._componedor


class ComponedorQueFallaUnaVez:
    """Simula una falla de la libreria en el primer intento; el adaptador la traduciria a ActaNoComponible."""

    def __init__(self):
        self.fallas = 1

    def componer(self, datos):
        if self.fallas:
            self.fallas -= 1
            raise ActaNoComponible()
        return real.componer(datos)


w._generar_acta._componedor = ComponedorQueFallaUnaVez()
w.procesar(reloj())
reloj.avanzar(minutes=1)
w.procesar(reloj())
acta = acta_pr08(r)
print(" intentos:", [(i.numero, i.resultado) for i in r.listar_intentos(acta.id)], "| acta:", str(acta.estado))
print(" adaptador real con datos invalidos:", end=" ")
try:
    real.componer(None)
except ActaNoComponible as error:
    print("ActaNoComponible:", error.mensaje)

print("== ESC-CO")
a, c, r, b, n, q, al, w, reloj = app()
solicitar(c, ["PR-08"])
n.disponible = False
w.procesar(reloj())
print(" acta:", actas(r), "| enviados:", n.listar_enviados(), "| pendientes:", [x["destinatarios"] for x in n.listar_pendientes()])

print("== ESC-E2")
a, c, r, b, n, q, al, w, reloj = app()
ids = []
for k in range(500):
    r.agregar_estudiante(Estudiante(f"E-7{k:03d}", f"e7{k:03d}@universidad.edu.co"))
    r.agregar_practica(Practica(f"PE-{k:03d}", f"E-7{k:03d}", "EMP-ACME", "v1", EstadoPractica.EVALUADA, "T-400"))
    r.guardar_evaluacion(Evaluacion(f"EV-E{k:03d}", f"PE-{k:03d}", {"Responsabilidad": 5, "Trabajo en equipo": 5, "Calidad técnica": 5}, "", date(2026, 11, 10)))
    ids.append(f"PE-{k:03d}")
al.fallas_pendientes = 30
t0 = time.perf_counter()
estado, cuerpo = solicitar(c, ids)
segundos = time.perf_counter() - t0
solicitada = reloj()
print(f" HTTP {estado}; aceptada en {segundos:.3f} s; resultados en generación: {sum(1 for x in cuerpo['resultados'] if x['resultado'] == 'en generación')}")
generada_en = {}
for minuto in range(0, 15):
    w.procesar(reloj())
    for x in r.listar_actas():
        if str(x.estado) == "generada" and x.id not in generada_en:
            generada_en[x.id] = reloj() - solicitada
    reloj.avanzar(minutes=1)
todas = [x for x in r.listar_actas() if x.id_practica.startswith("PE-")]
pdfs_validos = sum(1 for x in todas if x.ruta_pdf and al.leer(x.ruta_pdf).startswith(b"%PDF-"))
generadas = [x for x in todas if str(x.estado) == "generada"]
errores = {s.id_acta for s in q.listar_errores()}
en_10 = sum(1 for x in generadas if generada_en[x.id] <= timedelta(minutes=10))
print(f" actas: {len(todas)} | generadas: {len(generadas)} | en errores_actas: {len(errores)} | generadas o en errores: {len(generadas) + len(errores)} de 500")
print(f" PDF validos (empiezan con %PDF-): {pdfs_validos}")
print(f" pendientes en la cola actas: {len(q.listar_actas())} | intentos fallidos: {sum(1 for i in r.listar_intentos() if i.resultado.startswith('fallido'))}")
print(f" generadas en 10 min o menos: {en_10} de 500 = {en_10 / 500:.1%} | maximo: {max(generada_en.values())}")
```
