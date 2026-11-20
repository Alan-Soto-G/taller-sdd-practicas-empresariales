# Vista física: diagrama de despliegue

> Dónde se ejecuta cada contenedor. Diagrama: [04-fisica.puml](../diagramas/04-fisica.puml). Para ingenieros de infraestructura. Notación: diagrama UML de despliegue (nodos, componentes y conexiones).

## 1. Presentación principal

Despliegue del Sistema de Gestión de Prácticas Empresariales sobre la infraestructura de servidores que la universidad ya tiene (S-01). Muestra los nodos, los contenedores que aloja cada uno y las conexiones con los sistemas externos.

Diagrama: [diagramas/04-fisica.puml](../diagramas/04-fisica.puml)

## 2. Catálogo de elementos

| Nodo | Contenedores que aloja | Características | Conexiones |
|------|------------------------|-----------------|------------|
| Servidor web [Ubuntu, Nginx] | Aplicación web | Sirve los archivos estáticos de la interfaz; único nodo expuesto a internet, para que las empresas accedan sin VPN (S-02) | Navegadores de estudiantes, tutores, coordinador y representantes (HTTPS); API de prácticas (proxy inverso, red interna) |
| Servidor de aplicaciones [Docker] | API de prácticas, Worker de actas | Cada contenedor se reinicia y se replica por separado; en el cierre de semestre se agregan réplicas de la API y del worker (ADR-009, R-02) | Directorio Activo / SSO (HTTPS), Servicio de correo (SMTP), broker, base de datos y almacenamiento (red interna) |
| Servidor de mensajería [Docker] | Broker de mensajes | Colas persistentes: los mensajes sobreviven a un reinicio (ADR-001) | API y Worker de actas (AMQP, red interna) |
| Servidor de base de datos | PostgreSQL | Solo accesible desde la red interna; respaldo diario (ADR-003) | API y Worker de actas (SQL, red interna) |
| Almacenamiento institucional | Repositorio de actas | Almacenamiento de archivos de la universidad, con su política de respaldo | Worker de actas (escribe) y API (lee) |

Todos los nodos están en la infraestructura de la universidad que administra la Oficina de TI, sin compra de hardware (S-01, RN-01).

## 3. Justificación

- S-01 y RN-01: todo corre en servidores existentes, sin costos de nube pública ni licencias (ADR-009).
- RT-02 y S-02: solo el servidor web queda expuesto, para que estudiantes y empresas entren desde cualquier red y dispositivo.
- ADR-001 y EAC-02: el broker tiene colas persistentes en un nodo propio; si el worker cae, ningún acta se pierde.
- EAC-01 y R-02: la API y el worker se replican en el servidor de aplicaciones solo durante el cierre de semestre.
- RT-01: la conexión con el Directorio Activo / SSO sale del servidor de aplicaciones por la red universitaria.
- Preocupación del Líder de Infraestructura TI: la base de datos y el broker no son accesibles desde fuera de la red interna.

## 4. Comportamiento

La secuencia de [CU-07](../diagramas/secuencias/cu07-generar-acta-final.puml) cruza los nodos: la API y el broker se comunican por la red interna, el worker escribe en el almacenamiento institucional y el correo sale por SMTP. La de [CU-06](../diagramas/secuencias/cu06-evaluar-practicante.puml) entra desde internet por el servidor web.

## 5. Vistas relacionadas

- [Procesos](02-procesos.md): cada contenedor de esa vista aparece en un nodo de esta.
- [Contexto](../contexto.md): cada sistema externo aparece con su protocolo.
- ADR-003: PostgreSQL y un almacenamiento separado para los PDF de las actas.
