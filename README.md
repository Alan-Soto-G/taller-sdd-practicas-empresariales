# Sistema de Gestión de Prácticas Empresariales

Taller de Arquitectura de Soluciones de Software (Universidad de Caldas): la Facultad de Ingenierías gestiona en un solo lugar las prácticas empresariales de 500 estudiantes y 50 tutores al año. El sistema reemplaza las hojas de Excel y el correo en la postulación a plazas, la asignación de tutor, el registro y la aprobación de horas, la evaluación de la empresa y la generación y aprobación electrónica del acta final.

El repositorio recorre el proceso completo, desde la visión hasta el código, con desarrollo guiado por especificaciones (SDD): cada caso de uso tiene su spec, su plan, sus tareas, su código y su validación con evidencia.

## Cómo leerlo (en este orden)

| Paso | Archivo | Tema |
|------|---------|------|
| 1 | [docs/vision.md](docs/vision.md) | Visión: objetivos (OB-01 a OB-04), alcance, stakeholders, restricciones, supuestos y riesgos |
| 2 | [docs/drivers.md](docs/drivers.md) | Drivers: catálogo de casos de uso (CU-01 a CU-14), escenarios de calidad (EAC-01 a EAC-05), restricciones, preocupaciones, matriz y escenarios (+1) |
| 3 | [docs/adr/](docs/adr/) | ADR-001 a ADR-012: una decisión por archivo, con alternativas y consecuencias |
| 4 | [docs/contexto.md](docs/contexto.md) y [docs/vistas/](docs/vistas/) | Vistas 4+1 con C4 y UML |
| 5 | [docs/diagramas/](docs/diagramas/) | Diagramas como código (PlantUML): contexto, vistas y secuencias de los casos de uso primarios |
| 6 | [docs/arquitectura.md](docs/arquitectura.md) | Documento de arquitectura: el mapa que enlaza todo, con la deuda técnica y el glosario |
| 7 | [AGENTS.md](AGENTS.md) y [prompts/](prompts/) | SDD: reglas permanentes y una instrucción por fase (especificar, planear, descomponer, implementar y validar) |
| 8 | [specs/](specs/) | Una carpeta por caso de uso (001 a 014) con `spec.md`, `plan.md`, `tasks.md` y `validacion.md` |
| 9 | [src/](src/) | Código en Python 3.12 con Clean Architecture: `dominio/`, `aplicacion/` e `infraestructura/` |

## Cadena de trazabilidad

OB-01 a OB-04 (visión) → EAC, restricciones y preocupaciones (drivers) → ADR-001 a ADR-012 → vistas y secuencias → arquitectura.md → CU-01 a CU-14 (catálogo de drivers.md, columna "Se especifica en") → specs 001 a 014 → tareas de cada spec (un commit por tarea, con su ID) → código en `src/` → validación escenario por escenario.

Cada eslabón cita al anterior por su ID.

## Arquitectura en breve

- **Monolito modular con Clean Architecture** (ADR-002): `dominio/` no depende de nada; los casos de uso de `aplicacion/` definen los puertos (`Protocol`) y `infraestructura/` los implementa. Hay módulos de Postulaciones, Asignación, Horas, Evaluación, Actas, Seguimiento y Configuración.
- **Acta final asíncrona** (ADR-001): la API solo registra el acta y la deja en la cola. El **Worker de actas** es un proceso aparte que compone el PDF (ReportLab, ADR-011), reintenta hasta 3 veces y manda a la cola de errores lo que no logra generar.
- **Acceso** (ADR-004, ADR-005): los usuarios institucionales entran con el SSO y un token de 15 minutos. El Representante de la Empresa no tiene cuenta: usa un enlace de un solo uso que vence a los 7 días.
- **Trazabilidad** (ADR-006): se auditan los cambios de estado, las aprobaciones (que reemplazan las firmas) y cada acceso rechazado.
- **Reglas como datos** (ADR-008): horas requeridas, carga máxima por tutor, criterios de evaluación y plantilla del acta.
- En esta etapa, PostgreSQL, el broker, el SSO, el correo y el repositorio de actas son **adaptadores en memoria o simulados** que implementan los mismos puertos.

## Estructura

```text
taller-sdd-practicas-empresariales/
├── AGENTS.md
├── README.md
├── docs/
│   ├── vision.md
│   ├── drivers.md
│   ├── contexto.md
│   ├── arquitectura.md
│   ├── adr/                  ADR-001 a ADR-012
│   ├── vistas/               01-logica, 02-procesos, 03-desarrollo, 04-fisica (.md)
│   └── diagramas/            contexto, 01 a 04 (.puml) y secuencias/ (cu01, cu03, cu04, cu06, cu07)
├── specs/
│   ├── 001-postularse-plaza-practica/   spec.md, plan.md, tasks.md, validacion.md
│   ├── 002-publicar-plaza-practica/ … 014-gestionar-empresas/   misma estructura
├── prompts/                  0-arranque.md y 1 a 5 (una por fase)
└── src/
    ├── dominio/              entidades y reglas del negocio (sin dependencias)
    ├── aplicacion/           casos de uso por módulo, DTO, errores y puertos
    ├── infraestructura/      controlador REST, validadores y adaptadores en memoria, ReportLab y openpyxl
    ├── main.py               composición de la API
    ├── worker.py             composición del Worker de actas
    └── requirements.txt      dependencias aprobadas por ADR
```

## Cómo ejecutarlo

Requiere Python 3.12 o superior.

```bash
python -m pip install -r src/requirements.txt   # reportlab (ADR-011) y openpyxl (ADR-012)
python src/main.py                              # API: una postulación de ejemplo (CU-01)
python src/worker.py                            # API + Worker: solicita y genera un acta final (CU-07)
```

En esta etapa no hay servidor HTTP: `ControladorRest` recibe y devuelve estructuras de Python que representan cada petición (por ejemplo, `POST /practicas/{id}/horas`). Tampoco hay carpeta de pruebas automatizadas (AGENTS.md): cada `specs/NNN-*/validacion.md` trae en su Anexo el script que ejecuta sus escenarios contra `construir()`, con la evidencia obtenida.

## Cómo ver los diagramas

Los diagramas son archivos `.puml` (PlantUML, texto versionable). Se pueden ver con la extensión de PlantUML en VS Code o pegándolos en un editor en línea como editor.plantuml.com. Las vistas de C4 usan la librería estándar de PlantUML (`!include <C4/...>`).

## Estado

| Elemento | Estado |
|----------|--------|
| Visión, drivers, ADR, contexto, vistas, secuencias y arquitectura.md | Completos |
| AGENTS.md y prompts/ | Completos |
| Spec, plan y tareas de los casos de uso CU-01 a CU-14 | Completos |
| Código en `src/` de los 14 casos de uso | Completo (adaptadores en memoria o simulados) |
| Validación de las specs 001 a 014 | Completa: todos los escenarios cumplen, con evidencia y regresión de los anteriores |

## Notas para quien consulta

- ADR-011 (ReportLab para el PDF del acta) resolvió la deuda DT-05, y ADR-012 (openpyxl para el histórico en Excel) complementa ADR-008. Ambas librerías son de código abierto (RN-01) y quedan detrás de un puerto, de modo que `aplicacion/` no las importa.
- Las validaciones de EAC-01 (300 registros de horas simultáneos) y EAC-02 (500 actas con fallas) se miden con la composición en memoria. La prueba de carga real sobre PostgreSQL (R-02) y la prueba de usuario de EAC-05 se hacen fuera de las specs.
- Las decisiones tomadas al especificar cada caso de uso, donde los documentos no decían nada, están en la cabecera "Decisiones de la revisión" de cada `spec.md`.
