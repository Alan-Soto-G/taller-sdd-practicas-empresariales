# Prácticas Empresariales

## 1. Problema u oportunidad

Actualmente, la Facultad de Ingenierías gestiona las prácticas empresariales de 500 estudiantes y la asignación de 50 tutores al año utilizando únicamente hojas de cálculo de Excel y correos electrónicos. Esta situación es altamente insatisfactoria porque el proceso manual genera cuellos de botella en la asignación de tutores, pérdida de información en hilos de correo, dificultades para hacer un seguimiento en tiempo real de las horas reportadas por los estudiantes y retrasos administrativos considerables en la recopilación de evaluaciones de las empresas y la posterior generación de las actas finales para el grado.

## 2. Objetivos de negocio

- OB-01: Reducir el tiempo promedio del ciclo administrativo de asignación de tutores a estudiantes en un 60% durante el primer semestre de uso.
- OB-02: Disminuir la tasa de inconsistencias o errores en el registro mensual de horas de práctica en un 95% para el cierre del año lectivo.
- OB-03: Reducir el esfuerzo del personal administrativo en la recolección de firmas y generación del acta final, pasando de un promedio de 3 días a menos de 4 horas por estudiante.
- OB-04: Incrementar el índice de satisfacción de las empresas aliadas respecto al proceso de evaluación y comunicación con la universidad en un 20% al finalizar el primer ciclo anual.

## 3. Alcance

El sistema SÍ incluye:

- Módulo de postulación de estudiantes a las plazas de práctica disponibles.
- Funcionalidad para la asignación ágil de los 50 tutores a los estudiantes correspondientes.
- Registro y seguimiento en tiempo real de las horas de práctica ejecutadas por los 500 estudiantes.
- Interfaz para que las empresas realicen la evaluación de desempeño del practicante.
- Generación y exportación automatizada del acta final de la práctica empresarial.

El sistema NO incluye:

- Gestión de pagos, nómina o afiliaciones a seguridad social de los estudiantes en la empresa.
- Proceso de formalización jurídica de convenios marco entre nuevas empresas y la universidad (el sistema operará sobre las empresas ya aliadas).
- Bolsa de empleo para egresados o gestión de otras modalidades de grado (como tesis, monografías o diplomados).
- Módulo de entrevistas o pruebas psicotécnicas de selección interna de las empresas.

## 4. Stakeholders

| Rol | Tipo | Preocupaciones | Poder | Interés |
|---|---|---|---|---|
| Coordinador de Prácticas | Negocio | Facilidad de uso, centralización de la información, automatización de actas finales y generación de reportes precisos. | Alto | Alto |
| Estudiante | Negocio | Interfaz amigable para reportar sus horas fácilmente, visibilidad del estado de su acta y evaluaciones. | Medio | Alto |
| Tutor / Docente | Negocio | Visibilidad ágil del avance de sus estudiantes asignados sin sobrecarga administrativa. | Medio | Medio |
| Representante de la Empresa | Negocio | Rapidez para calificar al estudiante y no tener que instalar software adicional para evaluar. | Medio | Medio |
| Administrador de Base de Datos (DBA) | Técnico | Modelado de datos eficiente para migraciones futuras e integridad en transacciones concurrentes de 500 estudiantes. | Alto | Medio |
| Arquitecto de Software | Técnico | Escalabilidad del sistema, definición de la pila tecnológica y seguridad de la información. | Alto | Alto |
| Líder de Infraestructura TI | Técnico | Consumo de recursos en los servidores de la facultad, facilidad de despliegue y cumplimiento de políticas de red. | Alto | Medio |

## 5. Restricciones

- RT-01: El sistema debe integrarse obligatoriamente con el Directorio Activo (o sistema SSO) actual de la universidad para el inicio de sesión. Origen: Oficina de Tecnologías de la Información (TI) de la universidad, para cumplir con las políticas unificadas de seguridad y auditoría institucional.
- RT-02: El aplicativo debe ser 100% accesible vía web y contar con un diseño responsivo para móviles. Origen: Arquitectura de Software, para garantizar que estudiantes y tutores puedan registrar y aprobar horas desde cualquier dispositivo sin requerir instalaciones en equipos externos (como los de las empresas).
- RN-01: El desarrollo y despliegue del sistema no puede exceder el presupuesto asignado para la vigencia fiscal actual de la facultad. Origen: Decanatura de la Facultad de Ingenierías, debido a las limitaciones anuales del presupuesto universitario.
- RN-02: La primera versión funcional debe estar en producción a más tardar en 4 meses, antes de iniciar el próximo semestre académico. Origen: Coordinación de Prácticas, para evitar un empalme caótico y garantizar que el nuevo grupo de 500 estudiantes inicie el proceso 100% digital.

## 6. Supuestos y riesgos iniciales

Supuestos:

- S-01: Se asume que la universidad ya dispone de la infraestructura de servidores o nube necesaria para alojar el sistema, por lo que no se contempla presupuesto para compra de hardware.
- S-02: Se asume que las empresas aliadas tienen conexión a internet y permitirán a sus supervisores acceder a plataformas web externas para evaluar a los estudiantes (sin bloqueos de firewall corporativo).
- S-03: Se supone que los 50 tutores tienen dentro de su carga académica un tiempo oficial asignado para revisar el sistema, por lo que no exigirán pagos extra por el uso de una nueva plataforma.
- S-04: Se asume que se podrá extraer la información histórica o bases de datos base desde los archivos de Excel actuales sin necesidad de limpieza extrema de datos.

Riesgos iniciales:

- R-01: Alta resistencia al cambio por parte de los tutores más antiguos o de los delegados de las empresas, quienes podrían insistir en seguir usando el correo electrónico por costumbre.
- R-02: Colapso temporal de la aplicación durante las semanas de cierre de semestre, debido a la concurrencia masiva de estudiantes subiendo reportes de horas de última hora y la generación simultánea de actas.
- R-03: Retrasos en la integración con el sistema de autenticación de la universidad (TI) debido a procesos administrativos internos, lo que podría comprometer la restricción de tiempo RN-02.
