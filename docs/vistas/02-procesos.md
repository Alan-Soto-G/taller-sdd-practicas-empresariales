# Vista de procesos: diagrama de contenedores

> Nivel 2 de C4: se abre la caja y se hace zoom, qué se ejecuta y cómo se comunica. Diagrama: [02-procesos.puml](../diagramas/02-procesos.puml). Para integradores del sistema. En este contexto un contenedor no es Docker: es cualquier cosa que se ejecuta o guarda datos por separado.

## 1. Presentación principal

Diagrama de contenedores del Sistema de Gestión de Prácticas Empresariales: Aplicación web, API de prácticas, Broker de mensajes, Worker de actas, PostgreSQL y Repositorio de actas, con los sistemas externos que cada uno consume.

Diagrama: [diagramas/02-procesos.puml](../diagramas/02-procesos.puml)

## 2. Catálogo de elementos

| Elemento | Responsabilidad | Tecnología | Se comunica con |
|----------|-----------------|------------|-----------------|
| Aplicación web | Interfaz por rol: estudiante, tutor, coordinador y representante de empresa; adaptable a móviles (ADR-010) | Angular | API de prácticas (JSON / HTTPS); Directorio Activo / SSO (redirección de inicio de sesión) |
| API de prácticas | Reglas del proceso: postulación, asignación, horas, evaluación, actas y configuración (monolito modular, ADR-002) | Python | Aplicación web, PostgreSQL, Broker, Repositorio de actas (lee), Directorio Activo / SSO y Servicio de correo |
| Broker de mensajes | Guarda las solicitudes de acta hasta que el worker las procese; cola `actas` y cola `errores_actas` (ADR-001) | RabbitMQ | API (publica) y Worker de actas (entrega) |
| Worker de actas | Consolida horas, evaluación y datos de la práctica, compone el PDF con ReportLab (ADR-011), hace hasta 3 intentos y notifica | Python | Broker, PostgreSQL, Repositorio de actas y Servicio de correo |
| PostgreSQL | Postulaciones, prácticas, horas, evaluaciones, actas, aprobaciones, reglas, enlaces y auditoría (ADR-003, ADR-006) | PostgreSQL | API (SQL) y Worker de actas (SQL) |
| Repositorio de actas | PDF de las actas finales, listos para exportar | Almacenamiento institucional de archivos | Worker de actas (escribe) y API (lee) |

## 3. Justificación

- EAC-01 y EAC-02: el broker y el worker están separados de la API, así que la generación masiva no compite con el registro de horas (ADR-001).
- RN-02: una sola API como monolito modular (ADR-002).
- Integridad que exige el DBA y RN-01: PostgreSQL y repositorio institucional para los PDF (ADR-003).
- RT-01: la API valida contra el Directorio Activo / SSO la identidad de cada petición institucional (ADR-004).
- RT-02 y EAC-05: la aplicación web es adaptable y no exige instalación (ADR-010).
- ADR-005: la API envía por el Servicio de correo los enlaces de un solo uso a los representantes.

## 4. Comportamiento

- [cu01-postularse.puml](../diagramas/secuencias/cu01-postularse.puml): validación de cupo y elegibilidad en la API.
- [cu03-asignar-tutor.puml](../diagramas/secuencias/cu03-asignar-tutor.puml): asignación y notificación por correo.
- [cu04-registrar-horas.puml](../diagramas/secuencias/cu04-registrar-horas.puml): respuesta en menos de 2 s y rechazo del acceso ajeno.
- [cu06-evaluar-practicante.puml](../diagramas/secuencias/cu06-evaluar-practicante.puml): acceso con enlace de un solo uso.
- [cu07-generar-acta-final.puml](../diagramas/secuencias/cu07-generar-acta-final.puml): la API responde antes de que el worker genere el acta; reintentos con alt y loop.

## 5. Vistas relacionadas

- [Contexto](../contexto.md): de dónde vienen los actores y los sistemas externos.
- [Física](04-fisica.md): en qué servidor corre cada contenedor.
- [Desarrollo](03-desarrollo.md): cómo se organiza por dentro la API.
