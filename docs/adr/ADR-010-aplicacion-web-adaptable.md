# ADR-010: Construir la interfaz como una aplicación web adaptable de una sola página

## Estado

Aceptado (2026-11-19)

## Contexto

La restricción RT-02 obliga a que el sistema sea 100% web y responsivo para móviles. El escenario [EAC-05](../drivers.md#eac-05-capacidad-de-interacción-operabilidad) exige que un Representante de la Empresa evalúe desde el teléfono en menos de 5 minutos. El Estudiante (visión) pide una interfaz amigable para reportar horas, y OB-04 busca mejorar la satisfacción de las empresas en un 20%. RN-01 impide licencias.

## Alternativas consideradas

- **A) Aplicación móvil nativa más un sitio web.** Mejor experiencia en el teléfono; pero incumple RT-02 (exige instalar) y duplica el desarrollo en 4 meses (RN-02).
- **B) Aplicación web de una sola página (Angular) con diseño adaptable, que consume la API de prácticas.** Un solo código para escritorio y móvil, de código abierto; exige cuidar el rendimiento en conexiones lentas.
- **C) Páginas generadas en el servidor.** Menos código en el cliente; pero acopla la interfaz a la API (en contra de ADR-002) y vuelve más lenta la experiencia en formularios repetitivos, como el registro de horas.

## Decisión

Se elige la opción B, porque cumple RT-02 y EAC-05 con un solo código y sin licencias (RN-01). La interfaz se separa en vistas por rol (Estudiante, Tutor, Coordinador y Representante de la Empresa) y el formulario de evaluación se diseña primero para el móvil.

## Consecuencias

### Positivas

- Nadie instala nada; las empresas evalúan desde cualquier navegador (S-02).
- La API queda reutilizable para otros clientes en el futuro.

### Negativas y costos aceptados

- La aplicación web es un contenedor más que hay que construir y desplegar.
- El cumplimiento de EAC-05 solo se verifica con pruebas de usuario, no con pruebas automáticas.

### Riesgos asumidos

- El firewall de algunas empresas puede bloquear el dominio de la universidad (S-02 falso). Mitigación: verificarlo con las empresas aliadas antes del primer periodo.

### Vistas que modifica

[Procesos](../vistas/02-procesos.md) (Aplicación web) y [Física](../vistas/04-fisica.md) (Servidor web).
