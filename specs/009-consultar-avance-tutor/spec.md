# language: es
# Traza: CU-09, EAC-04, OB-02, ADR-002, ADR-004, ADR-006, ADR-007, ADR-008
# EAC: ningún EAC cita a CU-09 en su traza. El rechazo auditado del acceso ajeno sale de ADR-004 ("solo la
#      consultan su titular, su tutor asignado ...") y ADR-006, con la misma medida que EAC-04.
# Fuentes: docs/drivers.md (CU-09: "consulta de datos que ya están en el sistema"), visión (el Tutor quiere
#          "visibilidad ágil del avance de sus estudiantes asignados"), contexto (el Tutor consulta su avance),
#          vista de desarrollo (Módulo Seguimiento: CU-09 a CU-11; usa en solo lectura los Módulos Horas y
#          Actas), vista lógica (Práctica: horas aprobadas; ReglaPractica: horas requeridas).
#
# Decisiones de la revisión (se eligió la opción más simple, coherente con los ADR y con CU-01 a CU-08):
# - El Tutor consulta el avance de todas sus prácticas asignadas, o el de una sola práctica suya. Por cada
#   práctica ve el estudiante, el estado, las horas aprobadas, las horas requeridas de la versión de
#   ReglaPractica de la práctica (ADR-008), las horas reportadas pendientes de aprobar y el porcentaje de
#   avance (horas aprobadas sobre requeridas, entero redondeado hacia abajo, máximo 100).
# - Solo el rol Tutor usa CU-09. Otro rol, o un Tutor que pide una práctica que no tiene asignada, recibe
#   "acceso denegado" y el intento se audita (ADR-004, ADR-006). Las consultas exitosas no se auditan: no
#   cambian estado (ADR-006 audita cambios de estado, aprobaciones y accesos rechazados).
# - Se listan todas las prácticas del Tutor, en cualquier estado, ordenadas por id.
# - Los datos de este CU se precargan con ids propios ("T-500", "PR-10", "PR-11") para no alterar los
#   Antecedentes de CU-01 a CU-08.
Característica: Consultar el avance de los estudiantes asignados
  Como Tutor autenticado por el SSO institucional
  quiero ver el avance de horas de las prácticas que tengo asignadas
  para hacer seguimiento a mis estudiantes sin pedir reportes por correo

  Antecedentes:
    Dado la ReglaPractica "v1" con 160 horas requeridas
    Y el Tutor "T-500" autenticado por el SSO con el rol Tutor
    Y la Practica "PR-10" del Estudiante "E-1010" en estado "en curso" con el Tutor "T-500", con 3 registros aprobados de 20 horas y 1 registro reportado de 20 horas
    Y la Practica "PR-11" del Estudiante "E-1011" en estado "en curso" con el Tutor "T-500", sin registros de horas

  Escenario: Flujo básico - el Tutor consulta el avance de sus prácticas
    Cuando el Tutor "T-500" consulta el avance de sus estudiantes
    Entonces recibe 2 prácticas, "PR-10" y "PR-11"
    Y para "PR-10": Estudiante "E-1010", estado "en curso", 60 horas aprobadas de 160, 20 horas pendientes de aprobar y 37% de avance
    Y para "PR-11": Estudiante "E-1011", estado "en curso", 0 horas aprobadas de 160, 0 horas pendientes y 0% de avance
    Y la bitácora de auditoría no tiene registros nuevos

  Escenario: Flujo alterno - el Tutor consulta una sola práctica suya
    Cuando el Tutor "T-500" consulta el avance de la Practica "PR-10"
    Entonces recibe solo la práctica "PR-10" con 60 horas aprobadas de 160 y 37% de avance

  Escenario: Flujo alterno - un tutor sin prácticas asignadas
    Dado el Tutor "T-200" autenticado por el SSO, sin prácticas asignadas
    Cuando el Tutor "T-200" consulta el avance de sus estudiantes
    Entonces recibe una lista vacía

  Escenario: Flujo alterno - cuentan las horas requeridas de la versión de la práctica (ADR-008)
    Dado la ReglaPractica "v2" con 200 horas requeridas
    Y la Practica "PR-12" del Estudiante "E-1012" en estado "en curso" con el Tutor "T-500", la regla "v2" y 2 registros aprobados de 50 horas
    Cuando el Tutor "T-500" consulta el avance de la Practica "PR-12"
    Entonces recibe 100 horas aprobadas de 200 y 50% de avance

  Escenario: EAC-04 - un tutor consulta una práctica que no tiene asignada
    Cuando el Tutor "T-500" consulta el avance de la Practica "PR-04", asignada al Tutor "T-300"
    Entonces la petición se rechaza con el error de aplicación "acceso denegado"
    Y la bitácora de auditoría tiene un registro del acceso rechazado con usuario "T-500", rol "Tutor", recurso la Practica "PR-04", acción "consultar avance" y la hora

  Escenario: Excepción - un usuario sin el rol Tutor consulta el avance (ADR-004, ADR-006)
    Dado el Estudiante "E-1010" autenticado por el SSO con el rol Estudiante
    Cuando el Estudiante "E-1010" consulta el avance de la Practica "PR-10"
    Entonces la petición se rechaza con el error de aplicación "acceso denegado"
    Y la bitácora de auditoría tiene un registro del acceso rechazado con usuario "E-1010", rol "Estudiante", recurso la Practica "PR-10", acción "consultar avance" y la hora

  Escenario: Excepción - la práctica no existe
    Cuando el Tutor "T-500" consulta el avance de la Practica "PR-99", que no existe
    Entonces la petición se rechaza con el error de aplicación "práctica no encontrada"

  Escenario: Excepción - petición con token vencido (ADR-004)
    Dado una consulta de avance con un token emitido hace 16 minutos
    Cuando la API recibe la petición
    Entonces la petición se rechaza por falta de autenticación
