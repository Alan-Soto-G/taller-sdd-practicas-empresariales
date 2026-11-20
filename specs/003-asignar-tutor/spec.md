# language: es
# Traza: CU-03, ESC-02, OB-01, PA-05, ADR-002, ADR-004, ADR-006, ADR-007, ADR-008
# EAC: ningún EAC de docs/drivers.md cita a CU-03 en su traza (EAC-04 cita CU-04, CU-05 y CU-10).
#      OB-01 (reducir 60% el ciclo de asignación) es un objetivo de negocio que se mide en el primer
#      semestre de uso, no un escenario comprobable con sí o no.
#      El rechazo auditado de roles no autorizados sale de ADR-004 y ADR-006, no de un EAC.
# Fuentes: docs/drivers.md (CU-03: "reparte 500 estudiantes entre 50 tutores respetando la carga máxima de
#          cada uno"), secuencia cu03-asignar-tutor.puml (ESC-02), vista lógica (Tutor, ReglaPractica,
#          ciclo de vida de la Práctica: "sin tutor" -> "en curso"), ADR-006 (auditar cambios de estado de
#          Práctica), ADR-007 (el correo fallido no revierte la operación), ADR-008 (carga máxima como dato).
#
# Decisiones de la revisión (se eligió la opción más simple, coherente con los ADR y con CU-01 y CU-02):
# - La carga máxima por tutor es un dato de la ReglaPractica (ADR-008). En esta etapa se precarga la
#   ReglaPractica "v1" con carga máxima 2 (dato de los Antecedentes); su valor real lo fija el Coordinador.
# - La carga actual de un tutor cuenta sus prácticas en cualquier estado distinto de "cerrada".
# - La carga máxima se toma de la ReglaPractica vigente al momento de asignar, como en la secuencia ESC-02:
#   es un límite del tutor, no de la práctica. La versión de ReglaPractica que conserva cada Practica
#   (vista lógica) sigue mandando para sus horas requeridas y su plantilla del acta.
# - Si el cupo no alcanza para todas las prácticas seleccionadas, se asignan en el orden de selección hasta
#   llenar el cupo; las demás quedan "no asignada: tutor sin cupo". No se rechaza el lote completo.
# - Solo se asignan prácticas en estado "sin tutor". Reasignar (cambiar) el tutor queda fuera de alcance.
# - Una práctica inexistente o que ya tiene tutor solo se informa en su resultado; no rechaza la petición.
#   Un tutor inexistente sí rechaza la petición completa, porque ninguna práctica se puede asignar.
# - Si el correo falla, la asignación no se revierte y la notificación queda pendiente de reenvío (ADR-007).
# - La bitácora registra cada cambio de estado de Práctica y cada acceso rechazado (ADR-006); los
#   resultados "no asignada" no son cambios de estado y no se auditan (igual que en CU-01 y CU-02).
# - Las prácticas, los tutores y los estudiantes se precargan: crear la Práctica al aceptar una
#   Postulacion no pertenece a ningún caso de uso del catálogo (CU-01 lo deja fuera de alcance).
Característica: Asignar tutor a un estudiante
  Como Coordinador de Prácticas autenticado por el SSO institucional
  quiero asignar un tutor a una o varias prácticas "sin tutor", sin superar la carga máxima del tutor
  para que cada estudiante empiece su práctica acompañado y el ciclo de asignación sea más corto (OB-01)

  Antecedentes:
    Dado la ReglaPractica vigente "v1" con carga máxima por tutor de 2 prácticas
    Y el Tutor "T-200" con correo institucional "t200@universidad.edu.co"
    Y el Estudiante "E-1001" con correo institucional "e1001@universidad.edu.co"
    Y la Practica "PR-01" del Estudiante "E-1001" en estado "sin tutor"
    Y el Coordinador de Prácticas "C-01" autenticado por el SSO con el rol CoordinadorPracticas

  Escenario: Flujo básico - el Coordinador asigna un tutor con cupo a una práctica sin tutor
    Dado que el Tutor "T-200" tiene 0 prácticas asignadas
    Cuando el Coordinador "C-01" asigna el Tutor "T-200" a la Practica "PR-01"
    Entonces la Practica "PR-01" queda con el Tutor "T-200" y en estado "en curso"
    Y el Tutor "T-200" tiene 1 práctica asignada
    Y la bitácora de auditoría tiene un registro con usuario "C-01", rol "CoordinadorPracticas", recurso la Practica "PR-01", acción "cambiar estado de sin tutor a en curso" y la hora
    Y se envía un correo de asignación a "t200@universidad.edu.co" y a "e1001@universidad.edu.co"
    Y el Coordinador recibe el resultado "PR-01: asignada"

  Escenario: Flujo alterno - el Coordinador asigna el mismo tutor a varias prácticas a la vez
    Dado la Practica "PR-02" del Estudiante "E-1002" en estado "sin tutor"
    Y que el Tutor "T-200" tiene 0 prácticas asignadas
    Cuando el Coordinador "C-01" asigna el Tutor "T-200" a las Practicas "PR-01" y "PR-02"
    Entonces las Practicas "PR-01" y "PR-02" quedan con el Tutor "T-200" y en estado "en curso"
    Y el Tutor "T-200" tiene 2 prácticas asignadas
    Y la bitácora de auditoría tiene 2 registros nuevos de cambio de estado, uno por práctica
    Y el Coordinador recibe el resultado "PR-01: asignada" y "PR-02: asignada"

  Escenario: Excepción - el tutor ya alcanzó su carga máxima
    Dado que el Tutor "T-200" tiene 2 prácticas asignadas en estado "en curso"
    Cuando el Coordinador "C-01" asigna el Tutor "T-200" a la Practica "PR-01"
    Entonces la Practica "PR-01" sigue sin tutor y en estado "sin tutor"
    Y el Tutor "T-200" sigue con 2 prácticas asignadas
    Y no se envía ningún correo
    Y la bitácora de auditoría no tiene registros nuevos
    Y el Coordinador recibe el resultado "PR-01: no asignada: tutor sin cupo"

  Escenario: Flujo alterno - una práctica cerrada no cuenta en la carga del tutor
    Dado que el Tutor "T-200" tiene 1 práctica "en curso" y 1 práctica "cerrada"
    Cuando el Coordinador "C-01" asigna el Tutor "T-200" a la Practica "PR-01"
    Entonces la Practica "PR-01" queda con el Tutor "T-200" y en estado "en curso"
    Y el Coordinador recibe el resultado "PR-01: asignada"

  Escenario: Flujo alterno - el tutor tiene cupo solo para una parte de las prácticas seleccionadas
    Dado la Practica "PR-02" del Estudiante "E-1002" en estado "sin tutor"
    Y que el Tutor "T-200" tiene 1 práctica asignada
    Cuando el Coordinador "C-01" asigna el Tutor "T-200" a las Practicas "PR-01" y "PR-02", en ese orden
    Entonces la Practica "PR-01" queda con el Tutor "T-200" y en estado "en curso"
    Y la Practica "PR-02" sigue en estado "sin tutor"
    Y el Tutor "T-200" tiene 2 prácticas asignadas
    Y el Coordinador recibe el resultado "PR-01: asignada" y "PR-02: no asignada: tutor sin cupo"

  Escenario: Flujo alterno - el correo de notificación falla (ADR-007)
    Dado que el Tutor "T-200" tiene 0 prácticas asignadas
    Y que el Servicio de correo institucional no está disponible
    Cuando el Coordinador "C-01" asigna el Tutor "T-200" a la Practica "PR-01"
    Entonces la Practica "PR-01" queda con el Tutor "T-200" y en estado "en curso"
    Y la notificación de la asignación queda registrada como pendiente de reenvío
    Y el Coordinador recibe el resultado "PR-01: asignada"

  Escenario: Flujo alterno - un cambio de la carga máxima aplica a las asignaciones siguientes (ADR-008)
    Dado que el Tutor "T-200" tiene 2 prácticas asignadas
    Y que la ReglaPractica vigente cambió a "v2" con carga máxima por tutor de 3 prácticas
    Cuando el Coordinador "C-01" asigna el Tutor "T-200" a la Practica "PR-01"
    Entonces la Practica "PR-01" queda con el Tutor "T-200" y en estado "en curso"
    Y el Tutor "T-200" tiene 3 prácticas asignadas

  Escenario: Excepción - la práctica ya tiene tutor
    Dado la Practica "PR-03" del Estudiante "E-1003" en estado "en curso" con el Tutor "T-300"
    Y que el Tutor "T-200" tiene 0 prácticas asignadas
    Cuando el Coordinador "C-01" asigna el Tutor "T-200" a la Practica "PR-03"
    Entonces la Practica "PR-03" sigue con el Tutor "T-300" y en estado "en curso"
    Y el Tutor "T-200" sigue con 0 prácticas asignadas
    Y el Coordinador recibe el resultado "PR-03: no asignada: la práctica ya tiene tutor"

  Escenario: Excepción - la práctica no existe
    Dado que el Tutor "T-200" tiene 0 prácticas asignadas
    Cuando el Coordinador "C-01" asigna el Tutor "T-200" a la Practica "PR-99", que no existe
    Entonces el Coordinador recibe el resultado "PR-99: no asignada: práctica no encontrada"
    Y el Tutor "T-200" sigue con 0 prácticas asignadas

  Escenario: Excepción - el tutor no existe
    Cuando el Coordinador "C-01" asigna el Tutor "T-999", que no existe, a la Practica "PR-01"
    Entonces la asignación se rechaza con el error de aplicación "tutor no encontrado"
    Y la Practica "PR-01" sigue en estado "sin tutor"
    Y no se envía ningún correo

  Escenario: Excepción - un usuario sin el rol CoordinadorPracticas intenta asignar un tutor (ADR-004, ADR-006)
    Dado el Tutor "T-200" autenticado por el SSO con el rol Tutor
    Cuando el Tutor "T-200" intenta asignarse a sí mismo a la Practica "PR-01"
    Entonces la petición se rechaza con el error de aplicación "acceso denegado"
    Y la Practica "PR-01" sigue en estado "sin tutor"
    Y la bitácora de auditoría tiene un registro del acceso rechazado con usuario "T-200", rol "Tutor", recurso la Practica "PR-01", acción "asignar tutor" y la hora

  Escenario: Excepción - petición con token vencido (ADR-004)
    Dado una petición de asignación del Tutor "T-200" a la Practica "PR-01" con un token emitido hace 16 minutos
    Cuando la API recibe la petición
    Entonces la petición se rechaza por falta de autenticación
    Y la Practica "PR-01" sigue en estado "sin tutor"
