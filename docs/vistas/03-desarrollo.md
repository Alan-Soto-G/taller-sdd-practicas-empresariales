# Vista de desarrollo: diagrama de componentes

> Nivel 3 de C4 (componentes): se abre la aplicación y se hace zoom, sus bloques internos y responsabilidades. Se dibuja como diagrama UML de paquetes, un paquete por capa, para que las dependencias se lean de arriba hacia abajo. Diagrama: [03-desarrollo.puml](../diagramas/03-desarrollo.puml). Para programadores. Incluye las capas de Clean Architecture y la vista de usos sin ciclos.

## 1. Presentación principal

Diagrama de componentes del contenedor API de prácticas (monolito modular, ADR-002). Muestra, de arriba hacia abajo, los adaptadores de entrada (Controlador REST, Validador de token y Validador de enlace), los módulos de casos de uso, los puertos de `aplicacion/puertos/`, los adaptadores que los implementan y los sistemas reales que estos usan. Las dependencias que comparten todos los módulos (RepositorioPracticas y Bitacora) se dibujan una sola vez, desde el paquete; el detalle por módulo está en el catálogo.

Diagrama: [diagramas/03-desarrollo.puml](../diagramas/03-desarrollo.puml)

### Vista de usos (quién necesita a quién)

```text
Módulo Postulaciones ──usa──> dominio
Módulo Configuración ──usa──> dominio
Módulo Asignación ──usa (carga máxima por tutor)──> Módulo Configuración
Módulo Horas ──usa (horas requeridas)──> Módulo Configuración
Módulo Evaluación ──usa (criterios vigentes)──> Módulo Configuración
Módulo Actas ──usa (horas aprobadas)──> Módulo Horas
Módulo Actas ──usa (evaluación registrada)──> Módulo Evaluación
Módulo Seguimiento ──usa (solo lectura)──> Módulo Horas y Módulo Actas
Todos los módulos ──usan──> dominio
Prohibido: cualquier ciclo (por ejemplo, Módulo Horas usando Módulo Actas, o Módulo Configuración usando otro módulo)
```

- Incrementos: dominio, Configuración, Postulaciones y Asignación pueden entregarse antes que Horas; Horas y Evaluación, antes que Actas.
- Impacto: un cambio en Configuración obliga a revisar Asignación, Horas y Evaluación. Por eso la configuración es un dato (ADR-008) y su interfaz cambia poco.
- Los ciclos están prohibidos: son deuda técnica arquitectónica.

### Vista de capas (solo hacia adentro)

| Capa | Contenido | Puede usar |
|------|-----------|------------|
| infraestructura | Controlador REST, Validador de token, Validador de enlace, Adaptador SSO, Adaptador PostgreSQL, Publicador, Adaptador de correo, Adaptador de bitácora, Adaptador del repositorio de actas, Adaptador PDF (ReportLab) y Adaptador de Excel (openpyxl) | aplicacion y dominio (implementa los puertos) |
| aplicacion | Casos de uso (Postulaciones, Asignación, Horas, Evaluación, Actas, Seguimiento y Configuración) y puertos de salida en `aplicacion/puertos/` | dominio |
| dominio | Entidades y reglas: Practica, Postulacion, RegistroHoras, Evaluacion, ActaFinal, Aprobacion, ReglaPractica, EnlaceAcceso, entre otras | nada externo |

`main.py` (composición) conecta las capas: es lo único que las conoce todas. Si `dominio/` importa algo de `infraestructura/`, la arquitectura está rota. El Worker de actas es otro contenedor (ADR-001), pero reutiliza el mismo `dominio/`, el caso de uso de generación del Módulo Actas y los adaptadores de PostgreSQL, del repositorio de actas y de correo, con su propia composición.

## 2. Catálogo de elementos

| Componente | Tipo | Responsabilidad | Depende de |
|------------|------|-----------------|------------|
| Controlador REST | Adaptador de entrada | Recibe las peticiones HTTP y las traduce a casos de uso; convierte errores en respuestas unificadas (ADR-007) | Módulos de casos de uso, Validador de token, Validador de enlace |
| Validador de token | Adaptador de entrada | Valida el token de corta vida del usuario institucional y entrega su identidad y rol (ADR-004) | Puerto ProveedorIdentidad |
| Validador de enlace | Adaptador de entrada | Valida el enlace de un solo uso del representante y entrega una identidad acotada a una práctica y a una acción (ADR-005) | Puerto RepositorioPracticas |
| Módulo Postulaciones | Caso de uso | CU-01, CU-02 y CU-14: plazas, empresas y postulaciones | Puertos RepositorioPracticas y Bitacora |
| Módulo Asignación | Caso de uso | CU-03: asigna tutor respetando la carga máxima | Puertos RepositorioPracticas, Notificador y Bitacora; Módulo Configuración |
| Módulo Horas | Caso de uso | CU-04 y CU-05: registra y aprueba horas, con autorización por titularidad | Puertos RepositorioPracticas y Bitacora; Módulo Configuración |
| Módulo Evaluación | Caso de uso | CU-06: emite el enlace y registra la evaluación de la empresa | Puertos RepositorioPracticas, Notificador y Bitacora; Módulo Configuración |
| Módulo Actas | Caso de uso | CU-07, CU-08 y CU-12: solicita la generación, registra aprobaciones y exporta el acta | Puertos RepositorioPracticas, PublicadorActas, AlmacenActas, ComponedorActa (solo en el Worker, ADR-011), Notificador y Bitacora; Módulos Horas y Evaluación |
| Módulo Seguimiento | Caso de uso | CU-09, CU-10 y CU-11: consultas de avance, estado y reportes | Puerto RepositorioPracticas; Módulos Horas y Actas |
| Módulo Configuración | Caso de uso | Versiones de ReglaPractica y CriterioEvaluacion; importador de Excel de CU-13 (ADR-008) | Puertos RepositorioPracticas, LectorExcel (ADR-012) y Bitacora |
| Adaptador SSO | Adaptador | Implementa ProveedorIdentidad contra el Directorio Activo / SSO | Directorio Activo / SSO (OIDC / SAML) |
| Adaptador PostgreSQL | Adaptador | Implementa RepositorioPracticas | PostgreSQL (SQL) |
| Publicador | Adaptador | Implementa PublicadorActas sobre el broker | Broker de mensajes (AMQP) |
| Adaptador de correo | Adaptador | Implementa Notificador | Servicio de correo institucional (SMTP) |
| Adaptador de bitácora | Adaptador | Implementa Bitacora escribiendo en la tabla de auditoría (ADR-006) | PostgreSQL (SQL) |
| Adaptador del repositorio de actas | Adaptador | Implementa AlmacenActas (lectura de PDF para exportar) | Repositorio de actas (sistema de archivos) |
| Adaptador de Excel (openpyxl) | Adaptador | Implementa LectorExcel: lee las hojas del .xlsx y traduce un archivo ilegible a ArchivoNoValido (ADR-012, ADR-007) | Librería openpyxl |
| Adaptador PDF (ReportLab) | Adaptador | Implementa ComponedorActa: compone el PDF del acta y traduce sus fallas a ActaNoComponible (ADR-011, ADR-007) | Librería ReportLab |

En esta etapa del taller, cada adaptador externo tiene una versión en memoria o simulada que implementa el mismo puerto (`AGENTS.md`).

## 3. Justificación

- ADR-002 y RN-02: monolito modular con un módulo por grupo de casos de uso, abarcable en 4 meses.
- EAC-03 (mantenibilidad): un criterio de evaluación nuevo o un cambio de horas requeridas toca el Módulo Configuración y, como mucho, otro módulo (ADR-008).
- Regla de dependencia: los casos de uso definen los puertos; los adaptadores los implementan.
- Integridad y RN-01: PostgreSQL queda aislado en dos adaptadores (ADR-003).
- RT-01: el SSO queda aislado en el Adaptador SSO, lo que permite simularlo mientras TI habilita la integración (R-03, ADR-004).
- EAC-04: la autorización por titularidad está en los casos de uso, no en el controlador (ADR-004), y cada rechazo se audita (ADR-006).
- EAC-05: el Validador de enlace da acceso sin cuenta institucional (ADR-005).
- ADR-001: el Módulo Actas solo publica; nunca genera el PDF.
- ADR-007: los errores se traducen en los adaptadores y se responden de forma unificada en el controlador.

## 4. Comportamiento

- CU-04 dentro de la API: Controlador REST, Validador de token, Módulo Horas, Adaptador PostgreSQL y Adaptador de bitácora ([cu04-registrar-horas.puml](../diagramas/secuencias/cu04-registrar-horas.puml)).
- CU-07 dentro de la API: Módulo Actas y Publicador ([cu07-generar-acta-final.puml](../diagramas/secuencias/cu07-generar-acta-final.puml)).

## 5. Vistas relacionadas

- [Procesos](02-procesos.md): es el interior del contenedor API de prácticas.
- [Lógica](01-logica.md): los módulos operan sobre las entidades del modelo de dominio.
- Módulos: coincide con las capas descritas arriba.
