# language: es
# Traza: CU-04, ESC-03, EAC-01, EAC-04, OB-02, R-02, ADR-001, ADR-002, ADR-004, ADR-006, ADR-007
# Fuentes: docs/drivers.md (CU-04, EAC-01, EAC-04), secuencia cu04-registrar-horas.puml (ESC-03), vista
#          lógica (RegistroHoras: semana, horas, actividades, estado; "un solo registro por práctica y
#          semana"; Práctica "en curso": tiene tutor y el estudiante registra horas), ADR-004 (titularidad).
#
# Decisiones de la revisión (se eligió la opción más simple, coherente con los ADR y con CU-01 a CU-03):
# - La semana se escribe como semana ISO "AAAA-Wss" (por ejemplo "2026-W47"), con ss de 01 a 53.
# - "Horas fuera del rango permitido" (secuencia ESC-03): ningún documento fija un máximo semanal, así
#   que el rango es el físico de una semana: un entero de 1 a 168. No se inventa una regla del reglamento.
# - Las actividades son obligatorias (la secuencia dice "registra las horas y actividades de la semana").
# - Solo se registran horas en una Práctica "en curso" (vista lógica). En otro estado se rechaza con
#   "registro no válido" y el motivo "la práctica no está en curso".
# - Los rechazos por datos, por semana repetida o por estado responden 422 "registro no válido" con su
#   motivo (secuencia ESC-03, ADR-007); no se auditan, igual que los rechazos por regla de CU-01.
# - Orden de validación: rol, existencia de la práctica, titularidad, estado, datos y semana repetida.
#   Una práctica inexistente responde "práctica no encontrada".
# - Se audita la creación del RegistroHoras ("crear con estado reportado") y cada acceso rechazado (ADR-006).
# - EAC-01 en esta etapa se mide con la composición en memoria: 300 peticiones simultáneas. La prueba de
#   carga real sobre PostgreSQL antes del primer cierre (R-02) queda fuera de esta spec.
# - Corregir o borrar un registro "reportado" queda fuera de alcance; aprobarlo es CU-05.
Característica: Registrar horas de práctica
  Como Estudiante autenticado por el SSO institucional, titular de una práctica en curso
  quiero registrar las horas y actividades de cada semana
  para que mi tutor las apruebe y el seguimiento de mis horas sea consistente (OB-02)

  Antecedentes:
    Dado el Estudiante "E-1004" autenticado por el SSO con el rol Estudiante
    Y la Practica "PR-04" del Estudiante "E-1004" en estado "en curso" con el Tutor "T-300"
    Y el Estudiante "E-1001" autenticado por el SSO con el rol Estudiante
    Y la Practica "PR-01" del Estudiante "E-1001" en estado "sin tutor"

  Escenario: Flujo básico - el Estudiante registra las horas de una semana
    Dado que la Practica "PR-04" no tiene registros de horas
    Cuando el Estudiante "E-1004" registra 20 horas en la semana "2026-W47" de la Practica "PR-04" con las actividades "Desarrollo del módulo de reportes"
    Entonces se guarda un RegistroHoras de la Practica "PR-04", semana "2026-W47", 20 horas, esas actividades y estado "reportado"
    Y la bitácora de auditoría tiene un registro con usuario "E-1004", rol "Estudiante", recurso el RegistroHoras creado, acción "crear con estado reportado" y la hora
    Y el Estudiante recibe la confirmación "horas reportadas, pendientes de aprobación del tutor"

  Escenario: Flujo alterno - el Estudiante registra otra semana
    Dado que la Practica "PR-04" tiene un RegistroHoras de la semana "2026-W47"
    Cuando el Estudiante "E-1004" registra 18 horas en la semana "2026-W48" de la Practica "PR-04" con las actividades "Pruebas"
    Entonces la Practica "PR-04" tiene 2 RegistroHoras con estado "reportado"

  Escenario: Excepción - la semana ya tiene un registro
    Dado que la Practica "PR-04" tiene un RegistroHoras de la semana "2026-W47"
    Cuando el Estudiante "E-1004" registra 10 horas en la semana "2026-W47" de la Practica "PR-04" con las actividades "Otra vez"
    Entonces el registro se rechaza con el error de aplicación "registro no válido" y el motivo "la semana ya tiene un registro"
    Y la Practica "PR-04" sigue con 1 RegistroHoras de la semana "2026-W47"

  Esquema del escenario: Excepción - las horas o los datos están fuera del rango permitido
    Cuando el Estudiante "E-1004" registra <horas> horas en la semana "<semana>" de la Practica "PR-04" con las actividades "<actividades>"
    Entonces el registro se rechaza con el error de aplicación "registro no válido" y el motivo "<motivo>"
    Y no se guarda ningún RegistroHoras

    Ejemplos:
      | horas | semana   | actividades | motivo                                                     |
      | 0     | 2026-W47 | Desarrollo  | las horas deben estar entre 1 y 168                        |
      | -5    | 2026-W47 | Desarrollo  | las horas deben estar entre 1 y 168                        |
      | 169   | 2026-W47 | Desarrollo  | las horas deben estar entre 1 y 168                        |
      | 20    | 2026-W47 |             | las actividades son obligatorias                           |
      | 20    | 2026-47  | Desarrollo  | la semana debe tener el formato AAAA-Wss (semana 01 a 53)  |
      | 20    | 2026-W54 | Desarrollo  | la semana debe tener el formato AAAA-Wss (semana 01 a 53)  |

  Escenario: Excepción - la práctica no está en curso
    Cuando el Estudiante "E-1001" registra 20 horas en la semana "2026-W47" de la Practica "PR-01" con las actividades "Inducción"
    Entonces el registro se rechaza con el error de aplicación "registro no válido" y el motivo "la práctica no está en curso"
    Y no se guarda ningún RegistroHoras

  Escenario: Excepción - la práctica no existe
    Cuando el Estudiante "E-1004" registra 20 horas en la semana "2026-W47" de la Practica "PR-99", que no existe, con las actividades "Desarrollo"
    Entonces el registro se rechaza con el error de aplicación "práctica no encontrada"
    Y no se guarda ningún RegistroHoras

  Escenario: EAC-04 - un estudiante intenta registrar horas en una práctica ajena
    Cuando el Estudiante "E-1001" intenta registrar 20 horas en la semana "2026-W47" de la Practica "PR-04", que pertenece a "E-1004"
    Entonces la petición se rechaza con el error de aplicación "acceso denegado"
    Y no se guarda ningún RegistroHoras
    Y la bitácora de auditoría tiene un registro del acceso rechazado con usuario "E-1001", rol "Estudiante", recurso la Practica "PR-04", acción "registrar horas" y la hora
    # Medida de EAC-04: el 100% de los intentos de acceso ajeno se rechaza y queda registrado con usuario, recurso y hora.

  Escenario: Excepción - un usuario sin el rol Estudiante intenta registrar horas (ADR-004, ADR-006)
    Dado el Tutor "T-300" autenticado por el SSO con el rol Tutor
    Cuando el Tutor "T-300" intenta registrar 20 horas en la semana "2026-W47" de la Practica "PR-04"
    Entonces la petición se rechaza con el error de aplicación "acceso denegado"
    Y no se guarda ningún RegistroHoras
    Y la bitácora de auditoría tiene un registro del acceso rechazado con usuario "T-300", rol "Tutor", recurso la Practica "PR-04", acción "registrar horas" y la hora

  Escenario: Excepción - petición con token vencido (ADR-004)
    Dado una petición de registro de horas de la Practica "PR-04" con un token emitido hace 16 minutos
    Cuando la API recibe la petición
    Entonces la petición se rechaza por falta de autenticación
    Y no se guarda ningún RegistroHoras

  Escenario: EAC-01 - 300 estudiantes registran sus horas al mismo tiempo en el cierre
    Dado 300 Estudiantes autenticados, cada uno titular de una Practica "en curso" sin registros de horas
    Cuando los 300 registran al mismo tiempo 20 horas en la semana "2026-W47" de su Practica
    Entonces el 95% o más de las confirmaciones llega en menos de 2 segundos
    Y hay exactamente 300 RegistroHoras con estado "reportado", uno por Practica: 0 perdidos y 0 duplicados

  Escenario: EAC-01 - el mismo registro llega dos veces al mismo tiempo
    Cuando el Estudiante "E-1004" envía dos veces al mismo tiempo 20 horas en la semana "2026-W47" de la Practica "PR-04"
    Entonces una petición se confirma y la otra se rechaza con el motivo "la semana ya tiene un registro"
    Y la Practica "PR-04" tiene exactamente 1 RegistroHoras de la semana "2026-W47"
