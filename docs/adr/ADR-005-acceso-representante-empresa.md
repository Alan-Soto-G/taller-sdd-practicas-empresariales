# ADR-005: Dar acceso al Representante de la Empresa con un enlace de un solo uso y con vencimiento

## Estado

Aceptado (2026-11-19)

## Contexto

El Representante de la Empresa evalúa al practicante (CU-06) y aprueba el acta final (CU-08), pero no tiene cuenta en el Directorio Activo de la universidad. RT-01 solo cubre a los usuarios institucionales. Su preocupación (visión) es calificar rápido y sin instalar software adicional (RT-02, S-02). El escenario [EAC-05](../drivers.md#eac-05-capacidad-de-interacción-operabilidad) exige que complete la evaluación en menos de 5 minutos, sin crear cuenta. El riesgo R-01 advierte que los delegados de las empresas podrían insistir en seguir usando el correo electrónico. La preocupación PA-02 pide resolver este segundo mecanismo de acceso.

## Alternativas consideradas

- **A) Crear cuentas institucionales para los representantes.** Un solo mecanismo de acceso; pero depende de trámites de TI para personas externas, retrasa el plazo (RN-02) y obliga al representante a recordar otra contraseña (aumenta R-01).
- **B) Usuario y contraseña propios del sistema para las empresas.** No depende de TI; pero obliga a registrarse, a custodiar contraseñas y agrega fricción que incumple EAC-05.
- **C) Enlace de un solo uso con vencimiento, enviado por correo.** El sistema genera un token aleatorio, ligado a una práctica y a una acción (evaluar o aprobar el acta), y lo envía al correo registrado del representante. Sin registro ni contraseña; la seguridad depende del buzón del representante.

## Decisión

Se elige la opción C, porque es la única que cumple EAC-05 y RT-02 sin chocar con RT-01. El enlace vence a los 7 días, se invalida al usarse y solo da acceso a la práctica y a la acción para las que se emitió. El Coordinador puede reemitirlo. Cada uso y cada intento con un enlace vencido o inválido se audita (ADR-006).

## Consecuencias

### Positivas

- El representante evalúa desde el correo y el móvil, sin cuenta ni instalación, lo que reduce la resistencia al cambio (R-01).
- No se almacenan contraseñas de personas externas.

### Negativas y costos aceptados

- La seguridad depende del correo del representante: quien tenga el enlace puede usarlo mientras esté vigente.
- Se agrega una dependencia del Servicio de correo institucional para entregar los enlaces.

### Riesgos asumidos

- El correo del representante registrado puede estar desactualizado. Mitigación: el Coordinador lo verifica al gestionar la empresa (CU-14) y puede reemitir el enlace.

### Vistas que modifica

[Desarrollo](../vistas/03-desarrollo.md) (Validador de enlace), [Lógica](../vistas/01-logica.md) (EnlaceAcceso), [Contexto](../contexto.md) (Representante de la Empresa y Servicio de correo) y la secuencia [CU-06](../diagramas/secuencias/cu06-evaluar-practicante.puml).
