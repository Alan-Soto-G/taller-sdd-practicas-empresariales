# language: es
# Traza: CU-01, ESC-01, ADR-002, ADR-004, ADR-006, ADR-007
# EAC: ningún EAC de docs/drivers.md cita a CU-01 en su traza (EAC-04 cita CU-04, CU-05 y CU-10).
#      El rechazo auditado de roles no autorizados sale de ADR-004 y ADR-006, no de un EAC.
#
# Decisiones de la revisión (se eligió la opción más simple):
# - Elegibilidad: el único requisito es no tener una Postulacion "aceptada" en el periodo de la plaza.
# - No hay ventana de fechas: se puede postular en cualquier momento a una plaza existente.
# - Un Estudiante tiene a lo sumo una Postulacion por Plaza, en cualquier estado.
# - No hay máximo de postulaciones "enviadas" por Estudiante.
# - Toda Empresa registrada es aliada con convenio vigente (alcance de la visión); no se valida el convenio.
# - La bitácora registra los cambios de estado y los accesos rechazados (ADR-006); los rechazos por regla
#   de negocio no se auditan.
# - El cupo se consume al aceptar la Postulacion, no al enviarla. Aceptar o rechazar una Postulacion
#   está fuera del alcance de CU-01.
Característica: Postularse a una plaza de práctica
  Como Estudiante autenticado por el SSO institucional
  quiero postularme a una plaza de práctica con cupos disponibles
  para iniciar mi práctica empresarial en el periodo

  Antecedentes:
    Dado el periodo académico "2026-2"
    Y la Empresa "Acme S.A.S." aliada con convenio vigente
    Y la Plaza "PL-01" de "Acme S.A.S." para el periodo "2026-2" con 2 cupos
    Y el Estudiante "E-1001" autenticado por el SSO con el rol Estudiante

  Escenario: Flujo básico - el Estudiante se postula a una plaza con cupos
    Dado que la Plaza "PL-01" tiene 1 postulación aceptada
    Y que el Estudiante "E-1001" no tiene postulaciones aceptadas en el periodo "2026-2"
    Cuando el Estudiante "E-1001" se postula a la Plaza "PL-01"
    Entonces se registra una Postulacion del Estudiante "E-1001" a la Plaza "PL-01" con estado "enviada" y la fecha de hoy
    Y la bitácora de auditoría tiene un registro con usuario "E-1001", rol "Estudiante", recurso la Postulacion creada, acción "crear con estado enviada" y la hora
    Y el Estudiante recibe la confirmación "postulación enviada"

  Escenario: Excepción - la plaza no tiene cupos disponibles
    Dado que la Plaza "PL-01" tiene 2 postulaciones aceptadas
    Cuando el Estudiante "E-1001" se postula a la Plaza "PL-01"
    Entonces la postulación se rechaza con el error de aplicación "postulación no permitida" y el motivo "la plaza no tiene cupos disponibles"
    Y no se registra ninguna Postulacion del Estudiante "E-1001"
    Y la bitácora de auditoría no tiene registros nuevos

  Escenario: Excepción - el Estudiante ya tiene una postulación aceptada en el periodo
    Dado que el Estudiante "E-1001" tiene una Postulacion "aceptada" a la Plaza "PL-02" del periodo "2026-2"
    Y que la Plaza "PL-01" tiene 0 postulaciones aceptadas
    Cuando el Estudiante "E-1001" se postula a la Plaza "PL-01"
    Entonces la postulación se rechaza con el error de aplicación "postulación no permitida" y el motivo "ya tienes una postulación aceptada en el periodo"
    Y no se registra una nueva Postulacion del Estudiante "E-1001"

  Escenario: Flujo alterno - una postulación aceptada en otro periodo no impide postularse
    Dado que el Estudiante "E-1001" tiene una Postulacion "aceptada" a una plaza del periodo "2026-1"
    Y que la Plaza "PL-01" tiene 0 postulaciones aceptadas
    Cuando el Estudiante "E-1001" se postula a la Plaza "PL-01"
    Entonces se registra una Postulacion del Estudiante "E-1001" a la Plaza "PL-01" con estado "enviada"

  Esquema del escenario: Excepción - el Estudiante ya se postuló a la misma plaza
    Dado que el Estudiante "E-1001" tiene una Postulacion "<estado>" a la Plaza "PL-01"
    Cuando el Estudiante "E-1001" se postula de nuevo a la Plaza "PL-01"
    Entonces la postulación se rechaza con el error de aplicación "postulación no permitida" y el motivo "ya te postulaste a esta plaza"
    Y el Estudiante "E-1001" sigue con 1 sola Postulacion a la Plaza "PL-01"

    Ejemplos:
      | estado    |
      | enviada   |
      | rechazada |

  Escenario: Flujo alterno - el Estudiante tiene postulaciones enviadas a otras plazas
    Dado que el Estudiante "E-1001" tiene una Postulacion "enviada" a la Plaza "PL-02" del periodo "2026-2"
    Y que la Plaza "PL-01" tiene 0 postulaciones aceptadas
    Cuando el Estudiante "E-1001" se postula a la Plaza "PL-01"
    Entonces se registra una Postulacion del Estudiante "E-1001" a la Plaza "PL-01" con estado "enviada"
    Y el Estudiante "E-1001" tiene 2 Postulaciones "enviadas" en el periodo "2026-2"

  Escenario: Excepción - la plaza no existe
    Cuando el Estudiante "E-1001" se postula a la Plaza "PL-99", que no existe
    Entonces la postulación se rechaza con el error de aplicación "plaza no encontrada"
    Y no se registra ninguna Postulacion

  Escenario: Excepción - un usuario sin el rol Estudiante intenta postularse (ADR-004, ADR-006)
    Dado el Tutor "T-200" autenticado por el SSO con el rol Tutor
    Cuando el Tutor "T-200" intenta postularse a la Plaza "PL-01"
    Entonces la petición se rechaza con el error de aplicación "acceso denegado"
    Y no se registra ninguna Postulacion
    Y la bitácora de auditoría tiene un registro del acceso rechazado con usuario "T-200", rol "Tutor", recurso la Plaza "PL-01", acción "postularse" y la hora

  Escenario: Excepción - petición con token vencido (ADR-004)
    Dado una petición de postulación a la Plaza "PL-01" con un token emitido hace 16 minutos
    Cuando la API recibe la petición
    Entonces la petición se rechaza por falta de autenticación
    Y no se registra ninguna Postulacion

  Escenario: Concurrencia - dos estudiantes se postulan cuando queda un solo cupo
    Dado que la Plaza "PL-01" tiene 1 postulación aceptada
    Y el Estudiante "E-1002" autenticado por el SSO con el rol Estudiante
    Cuando el Estudiante "E-1001" y el Estudiante "E-1002" se postulan a la Plaza "PL-01" al mismo tiempo
    Entonces se registran 2 Postulaciones con estado "enviada" a la Plaza "PL-01"
    Y la Plaza "PL-01" sigue con 1 postulación aceptada
