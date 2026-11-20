# language: es
# Traza: CU-08, EAC-04, OB-03, PA-04, ADR-002, ADR-004, ADR-005, ADR-006, ADR-007
# EAC: docs/drivers.md dice que en CU-08 "la trazabilidad se cubre con EAC-04", y docs/arquitectura.md
#      (sección 8) cita la spec 008 para EAC-04. CU-08 no es primario y no tiene diagrama de secuencia.
# Fuentes: vista lógica (Aprobacion: rol, usuario, fecha; tres por acta, de tutor, empresa y coordinador;
#          con las tres, el acta queda aprobada; Práctica "acta en trámite" -> "cerrada" cuando el acta tiene
#          las tres aprobaciones), ADR-006 (las aprobaciones electrónicas reemplazan las firmas y se auditan),
#          ADR-005 (el Representante accede con un enlace de un solo uso para "evaluar o aprobar el acta";
#          el Coordinador lo emite y puede reemitirlo), ADR-004 (autorización por rol y titularidad).
#
# Decisiones de la revisión (se eligió la opción más simple, coherente con los ADR y con CU-01 a CU-07):
# - Solo se aprueba un ActaFinal "generada" (CU-07). En otro estado: 409 "aprobación no permitida" con el
#   motivo "el acta no está generada".
# - El Tutor aprueba con su token del SSO y solo si es el tutor asignado de la práctica del acta. El
#   Coordinador aprueba con su token. Cualquier otro rol (incluido el Estudiante) recibe "acceso denegado".
# - El Representante aprueba con un EnlaceAcceso de la acción "aprobar acta", que el Coordinador emite para
#   el acta (como el enlace de evaluación de CU-06): vence a los 7 días, es de un solo uso y emitirlo de
#   nuevo invalida el anterior. Un enlace de "evaluar" no sirve para aprobar ("enlace inválido", ADR-005).
# - Cada rol aprueba una sola vez: 409 "aprobación no permitida" con el motivo "el rol <rol> ya aprobó el
#   acta". El orden de las tres aprobaciones es libre.
# - Con la tercera aprobación, el acta pasa a "aprobada" y la Práctica a "cerrada".
# - Se auditan cada Aprobacion ("aprobar acta"), el paso del acta a "aprobada", el de la Práctica a
#   "cerrada", cada acceso rechazado y cada intento con un enlace no válido (ADR-005, ADR-006).
# - No se rechaza un acta: quien no está de acuerdo no aprueba (ningún documento define el rechazo).
# - Los datos se precargan con ids propios ("PR-09", "AC-09") para no alterar los Antecedentes de CU-07.
Característica: Aprobar el acta final
  Como Tutor asignado, Representante de la Empresa o Coordinador de Prácticas
  quiero aprobar electrónicamente el acta final generada
  para cerrar la práctica sin recolectar firmas a mano, con un rastro verificable de cada aprobación (OB-03)

  Antecedentes:
    Dado la Practica "PR-09" del Estudiante "E-1009" en estado "acta en trámite", con el Tutor "T-400" y en la Empresa "EMP-ACME"
    Y el ActaFinal "AC-09" de la Practica "PR-09" en estado "generada", sin aprobaciones
    Y el RepresentanteEmpresa "R-01" de "EMP-ACME" con correo "representante@acme.example"
    Y el Tutor "T-400" y el Coordinador "C-01" autenticados por el SSO con sus roles

  Escenario: Flujo básico (1/3) - el Tutor asignado aprueba el acta
    Cuando el Tutor "T-400" aprueba el ActaFinal "AC-09"
    Entonces se registra una Aprobacion del acta "AC-09" con rol "Tutor", usuario "T-400" y la fecha
    Y el acta tiene 1 de 3 aprobaciones y sigue en estado "generada"
    Y la bitácora de auditoría tiene un registro con usuario "T-400", rol "Tutor", recurso el acta "AC-09", acción "aprobar acta" y la hora
    Y el Tutor recibe la confirmación "aprobación registrada"

  Escenario: Flujo básico (2/3) - el Coordinador emite el enlace de aprobación y el Representante aprueba
    Cuando el Coordinador "C-01" solicita la aprobación de la empresa para el ActaFinal "AC-09"
    Entonces se guarda un EnlaceAcceso de la Practica "PR-09" con la acción "aprobar acta", sin usar y con vencimiento a los 7 días
    Y se envía un correo con el enlace a "representante@acme.example"
    Y cuando el Representante aprueba con ese enlace, se registra una Aprobacion con rol "RepresentanteEmpresa" y usuario "R-01"
    Y el enlace queda usado
    Y la bitácora de auditoría tiene los registros de usuario "R-01" con las acciones "usar enlace de aprobación" y "aprobar acta"

  Escenario: Flujo básico (3/3) - la tercera aprobación cierra la práctica
    Dado que el ActaFinal "AC-09" tiene las aprobaciones del Tutor y del Representante
    Cuando el Coordinador "C-01" aprueba el ActaFinal "AC-09"
    Entonces el acta tiene 3 de 3 aprobaciones y pasa a estado "aprobada"
    Y la Practica "PR-09" pasa a estado "cerrada"
    Y la bitácora de auditoría tiene los registros con las acciones "aprobar acta", "cambiar estado de generada a aprobada" y "cambiar estado de acta en trámite a cerrada"

  Escenario: Excepción - el mismo rol aprueba dos veces
    Dado que el Tutor "T-400" ya aprobó el ActaFinal "AC-09"
    Cuando el Tutor "T-400" aprueba otra vez el ActaFinal "AC-09"
    Entonces la aprobación se rechaza con el error de aplicación "aprobación no permitida" y el motivo "el rol Tutor ya aprobó el acta"
    Y el acta sigue con 1 de 3 aprobaciones

  Esquema del escenario: Excepción - el acta no está generada
    Dado el ActaFinal "AC-10" de la Practica "PR-09" en estado "<estado>"
    Cuando el Coordinador "C-01" aprueba el ActaFinal "AC-10"
    Entonces la aprobación se rechaza con el error de aplicación "aprobación no permitida" y el motivo "el acta no está generada"
    Y no se registra ninguna Aprobacion

    Ejemplos:
      | estado        |
      | en generación |
      | con error     |

  Escenario: Excepción - el acta no existe
    Cuando el Coordinador "C-01" aprueba el ActaFinal "AC-99", que no existe
    Entonces la aprobación se rechaza con el error de aplicación "acta no encontrada"

  Escenario: EAC-04 - un tutor que no está asignado intenta aprobar el acta
    Dado el Tutor "T-300" autenticado por el SSO con el rol Tutor, que no está asignado a la Practica "PR-09"
    Cuando el Tutor "T-300" intenta aprobar el ActaFinal "AC-09"
    Entonces la petición se rechaza con el error de aplicación "acceso denegado"
    Y no se registra ninguna Aprobacion
    Y la bitácora de auditoría tiene un registro del acceso rechazado con usuario "T-300", rol "Tutor", recurso el acta "AC-09", acción "aprobar acta" y la hora
    # Medida de EAC-04: el 100% de los intentos de acceso ajeno se rechaza y queda registrado con usuario, recurso y hora.

  Escenario: Excepción - el Estudiante titular intenta aprobar su acta (ADR-004)
    Dado el Estudiante "E-1009" autenticado por el SSO con el rol Estudiante
    Cuando el Estudiante "E-1009" intenta aprobar el ActaFinal "AC-09"
    Entonces la petición se rechaza con el error de aplicación "acceso denegado"
    Y la bitácora de auditoría tiene un registro del acceso rechazado con usuario "E-1009", rol "Estudiante", recurso el acta "AC-09", acción "aprobar acta" y la hora

  Escenario: Excepción - un usuario sin el rol CoordinadorPracticas solicita el enlace de aprobación (ADR-004)
    Cuando el Tutor "T-400" solicita la aprobación de la empresa para el ActaFinal "AC-09"
    Entonces la petición se rechaza con el error de aplicación "acceso denegado"
    Y no se guarda ningún EnlaceAcceso

  Esquema del escenario: Excepción - el enlace no sirve para aprobar (ADR-005, ADR-006)
    Dado un enlace de la Practica "PR-09" que <condición>
    Cuando el Representante intenta aprobar con ese enlace
    Entonces la petición se rechaza con 410 y el motivo "<motivo>"
    Y no se registra ninguna Aprobacion
    Y la bitácora de auditoría tiene un registro del intento rechazado con la acción "usar enlace rechazado: <motivo>"

    Ejemplos:
      | condición                                 | motivo          |
      | se emitió para la acción "evaluar"        | enlace inválido |
      | ya se usó para aprobar                    | enlace usado    |
      | se emitió hace 8 días                     | enlace vencido  |

  Escenario: Excepción - petición con token vencido (ADR-004)
    Dado una aprobación del ActaFinal "AC-09" con un token emitido hace 16 minutos
    Cuando la API recibe la petición
    Entonces la petición se rechaza por falta de autenticación
    Y no se registra ninguna Aprobacion
