# language: es
# Traza: CU-05, EAC-04, OB-02, OB-03, ADR-002, ADR-004, ADR-006, ADR-007, ADR-008
# EAC: EAC-04 cita a CU-05 en su traza (acceso ajeno rechazado y registrado). CU-05 no es primario y no
#      tiene diagrama de secuencia; sigue la forma de cu04-registrar-horas.puml.
# Fuentes: docs/drivers.md (CU-05: "cambio de estado sobre registros ya existentes; la integridad se cubre
#          con EAC-04"), ADR-004 ("solo el tutor asignado aprueba sus horas"), vista lógica (RegistroHoras:
#          reportado, aprobado, rechazado; "aprobado no se modifica"; Práctica "horas completas": las horas
#          aprobadas alcanzan las horas requeridas de su ReglaPractica), ADR-006 (auditar cada aprobación),
#          ADR-008 (cada práctica conserva la versión de ReglaPractica con la que empezó).
#
# Decisiones de la revisión (se eligió la opción más simple, coherente con los ADR y con CU-01 a CU-04):
# - El Tutor revisa un RegistroHoras a la vez con la decisión "aprobar" o "rechazar". No se piden
#   observaciones al rechazar (ningún documento las menciona).
# - Solo se revisa un registro "reportado". Uno "aprobado" o "rechazado" ya no cambia: se responde 422
#   "registro no válido" con el motivo "el registro ya fue revisado" (reutiliza el error de CU-04).
#   Corregir un registro rechazado queda fuera de alcance (CU-04 no admite otro registro de la misma semana).
# - Las horas aprobadas de una práctica son la suma de sus registros "aprobados" (no se guardan aparte).
# - Al aprobar, si la Práctica está "en curso" y sus horas aprobadas alcanzan las horas requeridas de la
#   versión de ReglaPractica con la que empezó (ADR-008), la Práctica pasa a "horas completas".
# - Solo el Tutor asignado a la Práctica revisa (ADR-004). Cualquier otro usuario, con cualquier rol
#   (incluidos el Estudiante titular y el Coordinador), recibe "acceso denegado" y el intento se audita.
# - Se auditan el cambio de estado del RegistroHoras, el de la Práctica y cada acceso rechazado (ADR-006).
#   Los rechazos por regla (decisión inválida, registro ya revisado) no se auditan, como en CU-01 a CU-04.
# - Las prácticas y los registros de este escenario se precargan con ids propios ("PR-05", "RH-05") para
#   no alterar los Antecedentes de CU-04.
Característica: Aprobar horas reportadas
  Como Tutor asignado a una práctica, autenticado por el SSO institucional
  quiero aprobar o rechazar las horas que reporta mi estudiante cada semana
  para que solo cuenten las horas verificadas (OB-02) y la aprobación quede registrada en lugar de una firma (OB-03)

  Antecedentes:
    Dado la ReglaPractica "v1" con 160 horas requeridas
    Y el Tutor "T-300" autenticado por el SSO con el rol Tutor
    Y la Practica "PR-05" del Estudiante "E-1005" en estado "en curso" con el Tutor "T-300" y la regla "v1"
    Y el RegistroHoras "RH-05" de la Practica "PR-05", semana "2026-W46", 20 horas, en estado "reportado"

  Escenario: Flujo básico - el Tutor aprueba las horas reportadas
    Dado que la Practica "PR-05" tiene 0 horas aprobadas
    Cuando el Tutor "T-300" aprueba el RegistroHoras "RH-05"
    Entonces el RegistroHoras "RH-05" queda en estado "aprobado"
    Y la Practica "PR-05" tiene 20 horas aprobadas y sigue en estado "en curso"
    Y la bitácora de auditoría tiene un registro con usuario "T-300", rol "Tutor", recurso el RegistroHoras "RH-05", acción "cambiar estado de reportado a aprobado" y la hora
    Y el Tutor recibe la confirmación "horas aprobadas"

  Escenario: Flujo alterno - el Tutor rechaza las horas reportadas
    Cuando el Tutor "T-300" rechaza el RegistroHoras "RH-05"
    Entonces el RegistroHoras "RH-05" queda en estado "rechazado"
    Y la Practica "PR-05" tiene 0 horas aprobadas
    Y la bitácora de auditoría tiene un registro con usuario "T-300", recurso el RegistroHoras "RH-05" y acción "cambiar estado de reportado a rechazado"
    Y el Tutor recibe la confirmación "horas rechazadas"

  Escenario: Flujo alterno - la aprobación completa las horas requeridas
    Dado que la Practica "PR-05" tiene 140 horas aprobadas
    Cuando el Tutor "T-300" aprueba el RegistroHoras "RH-05"
    Entonces la Practica "PR-05" tiene 160 horas aprobadas y pasa a estado "horas completas"
    Y la bitácora de auditoría tiene un registro con recurso la Practica "PR-05" y acción "cambiar estado de en curso a horas completas"

  Escenario: Flujo alterno - cuentan las horas requeridas de la versión de la práctica, no las de la vigente (ADR-008)
    Dado que la ReglaPractica vigente es "v2" con 200 horas requeridas
    Y que la Practica "PR-05", que empezó con la regla "v1", tiene 140 horas aprobadas
    Cuando el Tutor "T-300" aprueba el RegistroHoras "RH-05"
    Entonces la Practica "PR-05" tiene 160 horas aprobadas y pasa a estado "horas completas"

  Esquema del escenario: Excepción - el registro ya fue revisado
    Dado que el RegistroHoras "RH-05" está en estado "<estado>"
    Cuando el Tutor "T-300" aprueba el RegistroHoras "RH-05"
    Entonces la revisión se rechaza con el error de aplicación "registro no válido" y el motivo "el registro ya fue revisado"
    Y el RegistroHoras "RH-05" sigue en estado "<estado>"

    Ejemplos:
      | estado    |
      | aprobado  |
      | rechazado |

  Escenario: Excepción - la decisión no es aprobar ni rechazar
    Cuando el Tutor "T-300" revisa el RegistroHoras "RH-05" con la decisión "pendiente"
    Entonces la revisión se rechaza con el error de aplicación "registro no válido" y el motivo "la decisión debe ser aprobar o rechazar"
    Y el RegistroHoras "RH-05" sigue en estado "reportado"

  Escenario: Excepción - el registro no existe
    Cuando el Tutor "T-300" aprueba el RegistroHoras "RH-99", que no existe
    Entonces la revisión se rechaza con el error de aplicación "registro de horas no encontrado"

  Escenario: EAC-04 - un tutor que no está asignado intenta aprobar las horas
    Dado el Tutor "T-200" autenticado por el SSO con el rol Tutor, que no está asignado a la Practica "PR-05"
    Cuando el Tutor "T-200" intenta aprobar el RegistroHoras "RH-05"
    Entonces la petición se rechaza con el error de aplicación "acceso denegado"
    Y el RegistroHoras "RH-05" sigue en estado "reportado"
    Y la bitácora de auditoría tiene un registro del acceso rechazado con usuario "T-200", rol "Tutor", recurso el RegistroHoras "RH-05", acción "aprobar horas" y la hora
    # Medida de EAC-04: el 100% de los intentos de acceso ajeno se rechaza y queda registrado con usuario, recurso y hora.

  Escenario: Excepción - el Estudiante titular intenta aprobar sus propias horas (ADR-004)
    Dado el Estudiante "E-1005" autenticado por el SSO con el rol Estudiante
    Cuando el Estudiante "E-1005" intenta aprobar el RegistroHoras "RH-05"
    Entonces la petición se rechaza con el error de aplicación "acceso denegado"
    Y el RegistroHoras "RH-05" sigue en estado "reportado"
    Y la bitácora de auditoría tiene un registro del acceso rechazado con usuario "E-1005", rol "Estudiante", recurso el RegistroHoras "RH-05", acción "aprobar horas" y la hora

  Escenario: Excepción - petición con token vencido (ADR-004)
    Dado una petición de aprobación del RegistroHoras "RH-05" con un token emitido hace 16 minutos
    Cuando la API recibe la petición
    Entonces la petición se rechaza por falta de autenticación
    Y el RegistroHoras "RH-05" sigue en estado "reportado"
