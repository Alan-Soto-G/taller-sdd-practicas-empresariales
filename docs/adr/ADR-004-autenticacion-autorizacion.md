# ADR-004: Autenticar con el SSO institucional y autorizar por rol y titularidad con tokens de corta vida

## Estado

Aceptado (2026-11-19)

## Contexto

La restricción RT-01 obliga a usar el Directorio Activo (o SSO) de la universidad para el inicio de sesión de los usuarios institucionales: Estudiante, Tutor y Coordinador de Prácticas. La preocupación PA-02 exige decidir cómo se protege cada práctica. El escenario [EAC-04](../drivers.md#eac-04-seguridad-confidencialidad-y-responsabilidad) exige que el 100% de los accesos ajenos se rechace y se registre. La API debe poder replicarse en el cierre de semestre sin compartir estado (ADR-002, ADR-009). El riesgo R-03 advierte que la integración con el SSO puede retrasarse.

## Alternativas consideradas

- **A) Sesiones en servidor tras el inicio de sesión en el SSO.** Fáciles de revocar; pero obligan a compartir el estado de sesión entre réplicas de la API.
- **B) Token firmado (JWT) de corta vida emitido tras la autenticación en el SSO (OIDC o SAML), con autorización por rol y titularidad en cada caso de uso.** La API valida el token sin consultar un almacén de sesiones; revocar antes del vencimiento es más difícil.
- **C) Usuario y contraseña propios del sistema.** Control total; pero incumple RT-01, duplica credenciales y aumenta la superficie de ataque.

## Decisión

Se elige la opción B, porque cumple RT-01 y EAC-04 sin estado compartido entre réplicas. La autorización se aplica en el caso de uso, no en el controlador. Toda Práctica pertenece a un Estudiante. Solo la consultan su titular, su tutor asignado y el Coordinador de Prácticas, y solo el tutor asignado aprueba sus horas. Cada acceso rechazado se audita (ADR-006). El acceso de los representantes de empresa, que no tienen cuenta institucional, se resuelve en ADR-005.

## Consecuencias

### Positivas

- La API se replica sin sesiones compartidas.
- No se almacenan contraseñas en el sistema; la identidad la garantiza TI.

### Negativas y costos aceptados

- Dependencia del SSO institucional: si cae, los usuarios internos no ingresan.
- Revocar un token antes de su vencimiento es costoso; se acota con una vida corta (15 minutos).

### Riesgos asumidos

- R-03: retrasos administrativos en la integración con el SSO. Mitigación: el puerto de identidad permite desarrollar con un adaptador simulado mientras TI habilita la integración.

### Vistas que modifica

[Desarrollo](../vistas/03-desarrollo.md) (Validador de token) y [Contexto](../contexto.md) (Directorio Activo / SSO como sistema externo).
