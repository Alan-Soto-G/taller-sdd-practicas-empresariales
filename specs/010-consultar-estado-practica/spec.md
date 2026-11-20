# language: es
# Traza: CU-10, EAC-04, OB-02, OB-03, ADR-002, ADR-004, ADR-006, ADR-007, ADR-008
# EAC: EAC-04 cita a CU-10 en su traza ("intenta consultar ... la evaluación o el acta de una práctica que
#      no le pertenece"); docs/arquitectura.md (sección 8) cita la spec 010 para EAC-04.
# Fuentes: docs/drivers.md (CU-10: "consulta simple; la confidencialidad se cubre con EAC-04"), visión (el
#          Estudiante quiere "visibilidad del estado de su acta y evaluaciones"), contexto (el Estudiante
#          consulta el estado de su práctica y de su acta), vista de desarrollo (Módulo Seguimiento: CU-09 a
#          CU-11; usa en solo lectura los Módulos Horas y Actas), vista lógica (Práctica, ActaFinal, Aprobacion).
#
# Decisiones de la revisión (se eligió la opción más simple, coherente con los ADR y con CU-01 a CU-09):
# - El Estudiante consulta todas sus prácticas o una sola. Por cada práctica ve la empresa, el tutor, el
#   estado, el resumen de horas (el mismo de CU-09, con las horas requeridas de su versión de
#   ReglaPractica, ADR-008), si la empresa ya registró la evaluación (sí o no, sin las calificaciones) y el
#   acta: su estado y cuántas de las 3 aprobaciones tiene, o "sin acta" si aún no se solicitó.
# - Solo el rol Estudiante usa CU-10 y solo sobre sus prácticas. Otro rol, o un Estudiante que pide una
#   práctica ajena, recibe "acceso denegado" y el intento se audita con la acción "consultar estado"
#   (EAC-04). Las consultas exitosas no se auditan (no cambian estado, ADR-006).
# - Se usan los datos ya precargados por CU-04, CU-07, CU-08 y CU-09 ("PR-08", "PR-09", "PR-10"); solo se
#   agrega el token del Estudiante "E-1008".
Característica: Consultar el estado de la práctica y del acta
  Como Estudiante autenticado por el SSO institucional
  quiero consultar el estado de mi práctica, de mis horas, de la evaluación y de mi acta final
  para saber qué me falta sin preguntar por correo, y sin que nadie más vea mi información (EAC-04)

  Antecedentes:
    Dado la Practica "PR-08" del Estudiante "E-1008" en estado "evaluada", con 160 horas aprobadas de 160 y su Evaluacion registrada
    Y la Practica "PR-10" del Estudiante "E-1010" en estado "en curso", con 60 horas aprobadas y 20 pendientes
    Y la Practica "PR-09" del Estudiante "E-1009" en estado "acta en trámite", con el ActaFinal "AC-09" "generada" y sin aprobaciones
    Y los Estudiantes "E-1008", "E-1009" y "E-1010" autenticados por el SSO con el rol Estudiante

  Escenario: Flujo básico - el Estudiante consulta su práctica evaluada
    Cuando el Estudiante "E-1008" consulta el estado de la Practica "PR-08"
    Entonces recibe la empresa "EMP-ACME", el tutor "T-400" y el estado "evaluada"
    Y 160 horas aprobadas de 160, 0 pendientes y 100% de avance
    Y "evaluación registrada: sí"
    Y "acta: sin acta"
    Y la bitácora de auditoría no tiene registros nuevos

  Escenario: Flujo alterno - práctica en curso, sin evaluación ni acta
    Cuando el Estudiante "E-1010" consulta el estado de la Practica "PR-10"
    Entonces recibe el estado "en curso", 60 horas aprobadas de 160, 20 pendientes y 37% de avance
    Y "evaluación registrada: no" y "acta: sin acta"

  Escenario: Flujo alterno - práctica con el acta esperando aprobaciones
    Cuando el Estudiante "E-1009" consulta el estado de la Practica "PR-09"
    Entonces recibe el estado "acta en trámite"
    Y el acta "AC-09" en estado "generada" con 0 de 3 aprobaciones

  Escenario: Flujo alterno - el Estudiante consulta todas sus prácticas
    Cuando el Estudiante "E-1010" consulta el estado de sus prácticas sin indicar una
    Entonces recibe 1 práctica, "PR-10"

  Escenario: EAC-04 - un estudiante intenta consultar la práctica de otro
    Cuando el Estudiante "E-1010" consulta el estado de la Practica "PR-08", que pertenece a "E-1008"
    Entonces la petición se rechaza con el error de aplicación "acceso denegado"
    Y la bitácora de auditoría tiene un registro del acceso rechazado con usuario "E-1010", rol "Estudiante", recurso la Practica "PR-08", acción "consultar estado" y la hora
    # Medida de EAC-04: el 100% de los intentos de acceso ajeno se rechaza y queda registrado con usuario, recurso y hora.

  Escenario: Excepción - un usuario sin el rol Estudiante usa CU-10 (ADR-004, ADR-006)
    Dado el Tutor "T-500" autenticado por el SSO con el rol Tutor
    Cuando el Tutor "T-500" consulta el estado de la Practica "PR-10"
    Entonces la petición se rechaza con el error de aplicación "acceso denegado"
    Y la bitácora de auditoría tiene un registro del acceso rechazado con usuario "T-500", rol "Tutor", recurso la Practica "PR-10", acción "consultar estado" y la hora

  Escenario: Excepción - la práctica no existe
    Cuando el Estudiante "E-1010" consulta el estado de la Practica "PR-99", que no existe
    Entonces la petición se rechaza con el error de aplicación "práctica no encontrada"

  Escenario: Excepción - petición con token vencido (ADR-004)
    Dado una consulta de estado con un token emitido hace 16 minutos
    Cuando la API recibe la petición
    Entonces la petición se rechaza por falta de autenticación
