# AGENTS.md: Sistema de Prácticas Empresariales

Reglas permanentes del proyecto. Se le entregan al agente al inicio de cada sesión junto con `docs/arquitectura.md`. Es corto: enlaza a `docs/` en lugar de copiar su contenido.

## Fuentes de verdad

- `docs/arquitectura.md`: mapa de visión, drivers, ADR, vistas y glosario.
- `docs/drivers.md`, sección 1: catálogo de casos de uso. Es la lista de funcionalidades del sistema.
- `specs/`: una carpeta por caso de uso del catálogo, con el mismo número (CU-03 → `specs/003-...`), con `spec.md`, `plan.md`, `tasks.md` y `validacion.md`. La columna "Se especifica en" del catálogo enlaza cada caso de uso con su carpeta.
- Si el código contradice una especificación, gana la especificación. Si la especificación parece incorrecta, detenerse y preguntar.
- Los ADR no se editan: una decisión nueva se escribe como ADR nuevo que reemplaza al anterior.

## Arquitectura

- Monolito modular (ADR-002), con Clean Architecture por dentro.
- `dominio/` no importa nada de `aplicacion/` ni de `infraestructura/`.
- Puertos como `Protocol` en `aplicacion/puertos/` (los define el caso de uso; los implementa `infraestructura/`).

## Convenciones de código

- Python 3.12; una clase por archivo; sin `__init__.py`.
- DTO en la entrada y la salida de los casos de uso.
- Nombres según el glosario (sección 10 de `docs/arquitectura.md`).
- Sin base de datos real ni servicios externos reales en esta etapa: adaptadores en memoria o simulados.
- Sin carpeta de pruebas automatizadas en esta etapa: la validación se hace escenario por escenario, con evidencia.

---

## Forma de trabajar

- Una tarea de `tasks.md` a la vez.
- Al terminar: marcar la tarea, listar los archivos cambiados y detenerse.
- No inventar requisitos: lo que no esté en los documentos se marca en `spec.md` con `# [NECESITA ACLARACIÓN: <pregunta>]` o se pregunta.
- No agregar librerías que ningún ADR haya aprobado.
- Un commit por tarea, con el ID de la tarea en el mensaje.

---

## Flota de Obreros y Asignación de Tareas

Distribuye las subtareas según su complejidad para equilibrar cuotas y evitar saturar una sola herramienta. **Ejecuta un solo obrero a la vez (nunca en paralelo sobre el mismo repositorio)** para evitar conflictos de escritura:

### 1. GitHub Copilot CLI (`copilot`) — Obrero Principal (Lógica pesada y arquitectura)
- **Cuándo usarlo:** Módulos nuevos, controladores/servicios Express complejos, consultas Prisma, integraciones con APIs externas, refactors de múltiples archivos y tests de integración.
- **Selección de modelo:** usar `--model auto` (Copilot elige el modelo). Los nombres `claude-sonnet-5.5` y `claude-haiku-5.5` no están disponibles en la versión instalada (`Model "claude-haiku-5.5" is not available`).
- **Comando:**
  `copilot -p "<instrucción exacta con rutas, tipos y lógica>" --allow-all-tools --model auto`

### 2. Antigravity CLI (`agy`) — Obrero Secundario (Iteración, tests y documentación)
- **Cuándo usarlo:** Tests unitarios, anotaciones JSDoc/Swagger, actualización de colecciones Postman/README, endpoints CRUD sencillos y corrección de errores tras correr `npm run typecheck` o el linter.
- **Control de cuota:** Usa siempre su modelo por defecto (`gemini-3.8-flash`). **No** fuerces modelos Opus en `agy` para no agotar la cuota de Google AI Plus antes de su reinicio.
- **Comando:**
  `agy -p "<instrucción exacta con rutas, tipos y lógica>"`

### 3. OpenAI Codex CLI (`codex`) — Obrero Quirúrgico (Micro-tareas y respaldo)
- **Cuándo usarlo:** Exclusivamente para tareas pequeñas y autocontenidas en **1 solo archivo (<100 líneas)**: creación de interfaces/tipos TypeScript desde `src/docs/*-index.md`, DTOs, validadores, mappers o utilidades puras.
- **Control de cuota:** Cuenta gratuita con límite estricto; usa su modelo por defecto (`gpt-6-luna`) y nunca le pidas leer múltiples archivos.
- **Comando:**
  `codex exec -s workspace-write "<instrucción puntual sobre 1 archivo>"`
- **Nota operativa (CU-01):** la versión instalada no acepta `--full-auto`, y `--approve-for-me` no se puede combinar con `-s`. En T-01 escribió el archivo con BOM UTF-8 (desde PowerShell) y hubo que quitarlo; en T-02 se quedó colgado más de 5 minutos sin escribir nada y se detuvo. Pedir siempre "UTF-8 sin BOM", ejecutarlo con un `timeout` y, si se cuelga, pasar la subtarea a `copilot` o `agy` según el protocolo de fallback.

## Reglas de Orquestación, Balanceo y Fallback

1. **Contexto en Claude, ejecución en los obreros:** Lee tú los archivos necesarios y entrega al obrero elegido un prompt autosuficiente con rutas exactas, firmas de funciones e interfaces TypeScript. Prohibido pedirle a un obrero que explore todo el proyecto.
2. **Balanceo entre turnos:** Si una funcionalidad tiene varias subtareas medianas, altérnalas entre `copilot` (con `--model auto`) y `agy` para repartir el desgaste de cuotas.
3. **Protocolo de Fallback (Error 429 / Cuota agotada):**
   - Si un obrero falla por límite de cuota (`429`, *rate limit* o *quota exceeded*), **no detengas el plan**: reenvía inmediatamente la misma subtarea al siguiente obrero disponible (`copilot` ↔ `agy` → `codex`) y marca internamente al obrero agotado como no disponible por el resto de la sesión.
   - Si en la primera ejecución de `copilot` o `codex` algún flag de CLI difiere por versión instalada, ejecuta `<cli> --help` una sola vez para ajustar el comando no interactivo.
   - Si por alguna razón todos los Obreros se quedan con cuota agotada, tú (Claude Code) debes continuar con el desarrollo del plan.
4. **Auditoría obligatoria tras cada orden:**
   - Revisa `git diff` después de cada ejecución de cualquier obrero.
   - Si hay errores o desviaciones del diseño, envía una orden correctiva puntual al obrero que tenga mejor cuota disponible.