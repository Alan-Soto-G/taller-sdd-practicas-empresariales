# language: es
# Traza: CU-06, ESC-04, EAC-03, EAC-05, OB-04, RT-01, RT-02, S-02, R-01, PA-02, ADR-002, ADR-004, ADR-005,
#        ADR-006, ADR-007, ADR-008
# Fuentes: docs/drivers.md (CU-06, EAC-03, EAC-05), secuencia cu06-evaluar-practicante.puml (ESC-04), ADR-005
#          (enlace de un solo uso, ligado a una práctica y a una acción, vence a los 7 días, se invalida al
#          usarse, el Coordinador lo reemite, cada uso e intento rechazado se audita), vista lógica (Evaluacion:
#          una por práctica, califica todos los criterios de su ReglaPractica; CriterioEvaluacion: nombre,
#          escala; Práctica "horas completas" -> "evaluada"), ADR-008 (criterios como datos versionados).
#
# Decisiones de la revisión (se eligió la opción más simple, coherente con los ADR y con CU-01 a CU-05):
# - CU-06 tiene tres pasos, como en la secuencia ESC-04: el Coordinador emite el enlace, el Representante
#   abre el formulario y el Representante envía la evaluación. Abrir el formulario no consume el enlace;
#   enviarla sí.
# - Solo se emite el enlace de una Práctica en "horas completas" (secuencia). En otro estado: 409
#   "evaluación no permitida" con el motivo "la práctica no tiene las horas completas".
# - Cada Empresa tiene un RepresentanteEmpresa con su correo; el enlace se envía a ese correo. Gestionar
#   representantes es CU-14: aquí se precargan.
# - Emitir de nuevo el enlace de la misma práctica invalida el anterior (ADR-005, secuencia).
# - Un CriterioEvaluacion tiene nombre y escala: se califica con un entero de 1 a la escala. Los criterios
#   son un dato de la ReglaPractica con la que empezó la Práctica (ADR-008). La regla "v1" precarga tres
#   criterios con escala 5 (dato de prueba): "Responsabilidad", "Trabajo en equipo" y "Calidad técnica".
# - Una evaluación con datos inválidos (falta un criterio, criterio desconocido o calificación fuera de la
#   escala) responde 422 "evaluación no válida" con el motivo y no consume el enlace, para que el
#   Representante corrija. Las observaciones son opcionales.
# - Un enlace vencido, usado, invalidado o inexistente responde 410 con el mensaje de la secuencia
#   ("enlace vencido: solicite uno nuevo a la Coordinación") y el motivo, y el intento se audita (ADR-005,
#   ADR-006). Si el enlace no existe, se audita con usuario "desconocido".
# - Se auditan el uso del enlace, la creación de la Evaluacion y el cambio de estado de la Práctica a
#   "evaluada" (ADR-006). La emisión del enlace no es un cambio de estado de las entidades de ADR-006 y no se
#   audita; sí se audita el acceso rechazado de quien no es Coordinador.
# - Si el correo falla al emitir el enlace, el enlace queda guardado y el correo pendiente de reenvío (ADR-007).
# - EAC-05 (menos de 5 minutos para el 90% de los representantes) se mide con una prueba de usuario fuera de
#   las specs (docs/arquitectura.md, sección 8). Aquí se verifica la parte comprobable: el Representante
#   completa la evaluación con dos peticiones, sin cuenta ni token institucional.
# - EAC-03 (agregar un criterio) se verifica aquí como dato: una regla nueva con un criterio más no cambia
#   código y no altera las prácticas en curso.
Característica: Evaluar el desempeño del practicante
  Como Representante de la Empresa, sin cuenta institucional
  quiero evaluar a mi practicante desde el enlace que recibo por correo, sin instalar nada
  para entregar la evaluación de desempeño en pocos minutos (OB-04, EAC-05)

  Antecedentes:
    Dado la ReglaPractica "v1" con los criterios "Responsabilidad", "Trabajo en equipo" y "Calidad técnica", cada uno con escala 5
    Y el RepresentanteEmpresa "R-01" de la Empresa "EMP-ACME" con correo "representante@acme.example"
    Y la Practica "PR-06" del Estudiante "E-1006" en "EMP-ACME", en estado "horas completas", con la regla "v1"
    Y el Coordinador de Prácticas "C-01" autenticado por el SSO con el rol CoordinadorPracticas

  Escenario: Flujo básico (1/3) - el Coordinador emite el enlace de evaluación
    Cuando el Coordinador "C-01" solicita la evaluación de la Practica "PR-06"
    Entonces se guarda un EnlaceAcceso de la Practica "PR-06" con la acción "evaluar", sin usar y con vencimiento a los 7 días
    Y se envía un correo con el enlace a "representante@acme.example"
    Y el Coordinador recibe la confirmación "enlace de evaluación enviado"

  Escenario: Flujo básico (2/3) - el Representante abre el enlace y ve el formulario
    Dado un EnlaceAcceso vigente y sin usar de la Practica "PR-06" con la acción "evaluar"
    Cuando el Representante abre el enlace
    Entonces recibe el formulario de la Practica "PR-06" con los criterios "Responsabilidad", "Trabajo en equipo" y "Calidad técnica", cada uno con escala 5
    Y el enlace sigue sin usar

  Escenario: Flujo básico (3/3) - el Representante envía la evaluación
    Dado un EnlaceAcceso vigente y sin usar de la Practica "PR-06" con la acción "evaluar"
    Cuando el Representante envía las calificaciones "Responsabilidad" 5, "Trabajo en equipo" 4 y "Calidad técnica" 5 con las observaciones "Muy buen desempeño"
    Entonces se guarda una Evaluacion de la Practica "PR-06" con esas calificaciones y observaciones
    Y el enlace queda usado
    Y la Practica "PR-06" pasa a estado "evaluada"
    Y la bitácora de auditoría tiene los registros de usuario "R-01", rol "RepresentanteEmpresa", con las acciones "usar enlace de evaluación", "crear evaluación" y "cambiar estado de horas completas a evaluada", y la hora
    Y el Representante recibe la confirmación "evaluación enviada"

  Escenario: Excepción - la práctica no tiene las horas completas
    Dado la Practica "PR-04" en estado "en curso"
    Cuando el Coordinador "C-01" solicita la evaluación de la Practica "PR-04"
    Entonces la solicitud se rechaza con el error de aplicación "evaluación no permitida" y el motivo "la práctica no tiene las horas completas"
    Y no se guarda ningún EnlaceAcceso

  Escenario: Excepción - un usuario sin el rol CoordinadorPracticas solicita la evaluación (ADR-004, ADR-006)
    Dado el Tutor "T-300" autenticado por el SSO con el rol Tutor
    Cuando el Tutor "T-300" solicita la evaluación de la Practica "PR-06"
    Entonces la petición se rechaza con el error de aplicación "acceso denegado"
    Y no se guarda ningún EnlaceAcceso
    Y la bitácora de auditoría tiene un registro del acceso rechazado con usuario "T-300", rol "Tutor", recurso la Practica "PR-06", acción "emitir enlace de evaluación" y la hora

  Escenario: Excepción - petición del Coordinador con token vencido (ADR-004)
    Dado una solicitud de evaluación de la Practica "PR-06" con un token emitido hace 16 minutos
    Cuando la API recibe la petición
    Entonces la petición se rechaza por falta de autenticación
    Y no se guarda ningún EnlaceAcceso

  Escenario: Flujo alterno - el Coordinador reemite el enlace e invalida el anterior (ADR-005)
    Dado que el Coordinador "C-01" ya emitió un enlace de evaluación de la Practica "PR-06"
    Cuando el Coordinador "C-01" solicita otra vez la evaluación de la Practica "PR-06"
    Entonces se guarda un EnlaceAcceso nuevo y sin usar
    Y el enlace anterior queda invalidado: al abrirlo, la petición se rechaza con 410

  Escenario: Flujo alterno - el correo del enlace falla (ADR-007)
    Dado que el Servicio de correo institucional no está disponible
    Cuando el Coordinador "C-01" solicita la evaluación de la Practica "PR-06"
    Entonces se guarda el EnlaceAcceso de la Practica "PR-06"
    Y el correo con el enlace queda registrado como pendiente de reenvío
    Y el Coordinador recibe la confirmación "enlace de evaluación enviado"

  Esquema del escenario: Excepción - el enlace está vencido, usado o es inválido (ADR-005, ADR-006)
    Dado un enlace de la Practica "PR-06" que <condición>
    Cuando el Representante abre el enlace
    Entonces la petición se rechaza con 410 y el mensaje "enlace vencido: solicite uno nuevo a la Coordinación" con el motivo "<motivo>"
    Y la Practica "PR-06" no cambia de estado
    Y la bitácora de auditoría tiene un registro del intento rechazado con la acción "usar enlace rechazado: <motivo>" y la hora

    Ejemplos:
      | condición                            | motivo          |
      | fue emitido hace 8 días              | enlace vencido  |
      | ya se usó para enviar la evaluación  | enlace usado    |
      | no existe                            | enlace inválido |

  Esquema del escenario: Excepción - las calificaciones no son válidas
    Dado un EnlaceAcceso vigente y sin usar de la Practica "PR-06" con la acción "evaluar"
    Cuando el Representante envía las calificaciones <calificaciones>
    Entonces la evaluación se rechaza con el error de aplicación "evaluación no válida" y el motivo "<motivo>"
    Y no se guarda ninguna Evaluacion
    Y el enlace sigue sin usar

    Ejemplos:
      | calificaciones                                                              | motivo                                                    |
      | "Responsabilidad" 5 y "Trabajo en equipo" 4                                 | falta calificar el criterio Calidad técnica               |
      | "Responsabilidad" 6, "Trabajo en equipo" 4 y "Calidad técnica" 5            | la calificación de Responsabilidad debe estar entre 1 y 5 |
      | "Responsabilidad" 0, "Trabajo en equipo" 4 y "Calidad técnica" 5            | la calificación de Responsabilidad debe estar entre 1 y 5 |
      | las tres válidas y "Puntualidad" 5                                          | criterio desconocido: Puntualidad                         |

  Escenario: EAC-05 - el Representante evalúa sin cuenta ni instalación
    Dado un EnlaceAcceso vigente y sin usar de la Practica "PR-06" recibido por correo
    Cuando el Representante abre el enlace y envía la evaluación, sin token institucional
    Entonces la evaluación queda registrada con 2 peticiones (abrir el formulario y enviarlo)
    Y en ningún paso se pide cuenta, contraseña ni token del SSO
    # Medida de EAC-05: el 90% de los representantes de la prueba de usuario termina en menos de 5 minutos.
    # Esa prueba de usuario se hace fuera de las specs (docs/arquitectura.md, sección 8).

  Escenario: EAC-03 - un criterio nuevo se agrega como dato, sin cambiar código
    Dado que el Coordinador agrega la ReglaPractica "v2" con los tres criterios de "v1" y el criterio "Comunicación" con escala 5
    Y la Practica "PR-07" en estado "horas completas" con la regla "v2"
    Cuando el Representante abre el enlace de evaluación de la Practica "PR-07" y el de la Practica "PR-06"
    Entonces el formulario de "PR-07" tiene 4 criterios, incluido "Comunicación"
    Y el formulario de "PR-06", que empezó con "v1", sigue con 3 criterios
    Y el cambio no modificó ningún archivo de src/
