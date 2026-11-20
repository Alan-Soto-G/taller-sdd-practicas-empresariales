# Contexto del sistema: Sistema de Gestión de Prácticas Empresariales

> Nivel 1 de C4. El contexto no es una vista de 4+1: es el marco que encuadra a todas. Diagrama: [contexto.puml](diagramas/contexto.puml)

## 1. Presentación principal

El Sistema de Gestión de Prácticas Empresariales aparece como una caja negra, rodeada de las cuatro personas que lo usan y de los dos sistemas externos con los que se comunica. Responde: ¿qué hay afuera y cómo se comunica el sistema con ello?

Diagrama: [diagramas/contexto.puml](diagramas/contexto.puml)

## 2. Catálogo de elementos

| Elemento | Tipo | Rol o responsabilidad | Interacción con el sistema |
|----------|------|-----------------------|----------------------------|
| Estudiante | Persona | Se postula a plazas, registra sus horas y consulta el estado de su práctica y de su acta | Aplicación web (HTTPS), tras iniciar sesión en el SSO |
| Tutor | Persona | Aprueba las horas de sus estudiantes asignados, consulta su avance y aprueba el acta final | Aplicación web (HTTPS), tras iniciar sesión en el SSO |
| Coordinador de Prácticas | Persona | Publica plazas, asigna tutores, gestiona empresas, solicita y aprueba las actas y genera reportes | Aplicación web (HTTPS), tras iniciar sesión en el SSO |
| Representante de la Empresa | Persona | Evalúa el desempeño del practicante y aprueba el acta final, sin cuenta institucional | Aplicación web (HTTPS), con un enlace de un solo uso recibido por correo (ADR-005) |
| Sistema de Gestión de Prácticas Empresariales | Sistema en alcance | Gestiona postulación, asignación de tutor, seguimiento de horas, evaluación y acta final | Con todos los demás elementos |
| Directorio Activo / SSO | Sistema externo | Autentica a estudiantes, tutores y coordinador; lo administra la Oficina de TI (RT-01) | OIDC o SAML sobre HTTPS |
| Servicio de correo institucional | Sistema externo | Entrega las notificaciones y los enlaces de acceso a los representantes de empresa | SMTP |

## 3. Justificación

- CU-01, CU-03, CU-04, CU-06 y CU-07 (primarios) definen las cuatro personas y las dos integraciones.
- RT-01: la autenticación de los usuarios institucionales se delega al Directorio Activo / SSO, que no se controla y por eso aparece como sistema aparte (ADR-004).
- RT-02 y S-02: el Representante de la Empresa entra desde la web, sin instalar nada y sin cuenta institucional (ADR-005).
- Stakeholder: el Líder de Infraestructura TI necesita ver con qué servicios de la universidad se integra el sistema y por qué protocolo.
- Sin integraciones pagas de terceros (RN-01): las firmas del acta son aprobaciones electrónicas internas (ADR-006).

## 4. Comportamiento

Los escenarios (+1) empiezan aquí: [CU-06 evaluar al practicante](diagramas/secuencias/cu06-evaluar-practicante.puml) muestra el ingreso por enlace desde el correo, y [CU-04 registrar horas](diagramas/secuencias/cu04-registrar-horas.puml) muestra el ingreso de un usuario institucional autenticado por el SSO.

## 5. Vistas relacionadas

- [Procesos](vistas/02-procesos.md): qué contenedor habla con cada sistema externo.
- [Física](vistas/04-fisica.md): por qué red sale cada conexión.
