# language: es
# Traza: CU-07, ESC-05, EAC-02, OB-03, R-02, R-04, DT-01, DT-05, ADR-001, ADR-002, ADR-003, ADR-004, ADR-006,
#        ADR-007, ADR-008, ADR-011
# Fuentes: docs/drivers.md (CU-07, EAC-02), secuencia cu07-generar-acta-final.puml (ESC-05), ADR-001 (la API
#          solo encola; Worker de actas con hasta 3 intentos y esperas de 1 y 2 min; cola actas y cola
#          errores_actas), ADR-003 (PDF en el repositorio de actas, ruta en la base), vista lógica (ActaFinal:
#          en generación, generada, aprobada, con error; "solo se solicita con las horas requeridas aprobadas
#          y la evaluación registrada"; IntentoGeneracion máximo 3; Práctica "evaluada" -> "acta en trámite").
#
# Decisiones de la revisión (se eligió la opción más simple, coherente con los ADR y con CU-01 a CU-06):
# - CU-07 tiene dos partes, como en la secuencia ESC-05: la API registra la solicitud y encola (responde 202),
#   y el Worker de actas genera el acta después, con su propia composición (ADR-001, ADR-002).
# - Solo se solicita el acta de una Práctica "evaluada": su estado ya garantiza las horas requeridas
#   aprobadas (CU-05) y la evaluación registrada (CU-06). Al solicitarla, la Práctica pasa a "acta en trámite".
# - El Coordinador solicita varias actas a la vez; cada práctica tiene su resultado ("en generación" o
#   "no solicitada: <motivo>"), como en CU-03. Una práctica no evaluada o inexistente no rechaza el lote.
# - El PDF es real: ADR-011 (2026-11-20, resuelve DT-05) elige ReportLab detrás del puerto ComponedorActa. El
#   Worker consolida los datos de la práctica, las horas, la evaluación y la plantilla de su ReglaPractica
#   (ADR-008), compone el PDF y lo guarda en el AlmacenActas (en memoria en esta etapa). La primera versión de
#   esta spec usaba un documento simulado porque DT-05 estaba abierta.
# - Si el componedor falla, el adaptador lo traduce a "no se pudo componer el PDF del acta" (ADR-007, ADR-011) y
#   cuenta como un intento fallido, igual que la falla del repositorio de actas (la secuencia dice "falla al
#   consolidar o al componer el PDF").
# - La falla de generación se simula con el repositorio de actas no disponible al guardar el PDF; el
#   adaptador la traduce al error de aplicación "repositorio de actas no disponible" (ADR-007).
# - Reintentos (ADR-001): intento 1; si falla, se reencola para 1 min después; intento 2; si falla, para
#   2 min después; intento 3; si falla, la solicitud pasa a la cola errores_actas y el acta queda "con error".
#   Cada intento queda como IntentoGeneracion (exitoso o fallido con su motivo).
# - Reprocesar un acta "con error" queda fuera de alcance (DT-01: depende del Coordinador).
# - Al generarse el acta se avisa por correo al tutor, al representante de la empresa y al Coordinador que
#   el acta espera su aprobación (CU-08). Si el correo falla, el acta sigue "generada" y el aviso queda
#   pendiente de reenvío (ADR-007).
# - Se auditan la creación del ActaFinal, el cambio de la Práctica a "acta en trámite", el paso del acta a
#   "generada" o "con error" (el Worker audita como usuario "worker-actas", rol "WorkerActas") y cada acceso
#   rechazado (ADR-006).
# - La alerta de R-04 (más de 100 pendientes en la cola) es de operación y queda fuera de esta spec.
# - EAC-02 se mide con la composición en memoria y un reloj simulado para las esperas de 1 y 2 min.
Característica: Generar el acta final
  Como Coordinador de Prácticas autenticado por el SSO institucional
  quiero solicitar las actas finales de las prácticas evaluadas y que se generen en segundo plano
  para cerrar las prácticas sin recolectar firmas a mano (OB-03), sin que se pierda ningún acta en el cierre (EAC-02)

  Antecedentes:
    Dado la ReglaPractica "v1" con 160 horas requeridas y la plantilla "plantilla-acta-v1"
    Y la Practica "PR-08" del Estudiante "E-1008" en estado "evaluada", con el Tutor "T-400", 160 horas aprobadas y su Evaluacion registrada
    Y el RepresentanteEmpresa "R-01" de la Empresa "EMP-ACME" con correo "representante@acme.example"
    Y el Coordinador de Prácticas "C-01" con correo "coordinacion@universidad.edu.co", autenticado por el SSO con el rol CoordinadorPracticas

  Escenario: Flujo básico (1/2) - el Coordinador solicita el acta y la API solo la encola
    Cuando el Coordinador "C-01" solicita las actas de la Practica "PR-08"
    Entonces se registra un ActaFinal de la Practica "PR-08" en estado "en generación"
    Y la Practica "PR-08" pasa a estado "acta en trámite"
    Y la cola "actas" tiene una SolicitudActa de esa acta
    Y el repositorio de actas no tiene ningún PDF: la API no compone el acta (ADR-001)
    Y la bitácora de auditoría tiene los registros de usuario "C-01" con las acciones "crear con estado en generación" y "cambiar estado de evaluada a acta en trámite"
    Y el Coordinador recibe la respuesta 202 con el resultado "PR-08: en generación" y el mensaje "actas en generación; se le notificará"

  Escenario: Flujo básico (2/2) - el Worker de actas genera el acta
    Dado que la cola "actas" tiene la SolicitudActa del acta de la Practica "PR-08"
    Cuando el Worker de actas procesa la cola
    Entonces el repositorio de actas guarda el PDF del acta (un archivo PDF válido), con la plantilla "plantilla-acta-v1", las 160 horas aprobadas y la evaluación
    Y se registra el IntentoGeneracion 1 con resultado "exitoso"
    Y el ActaFinal queda en estado "generada" con la ruta del PDF
    Y se envía un correo a "t400@universidad.edu.co", "representante@acme.example" y "coordinacion@universidad.edu.co" avisando que el acta espera su aprobación
    Y la cola "actas" queda vacía

  Escenario: Excepción - la práctica no está evaluada
    Dado la Practica "PR-04" en estado "en curso"
    Cuando el Coordinador "C-01" solicita las actas de la Practica "PR-04"
    Entonces el Coordinador recibe el resultado "PR-04: no solicitada: la práctica no está evaluada"
    Y no se registra ningún ActaFinal y la cola "actas" queda vacía

  Escenario: Excepción - la práctica no existe
    Cuando el Coordinador "C-01" solicita las actas de la Practica "PR-99", que no existe
    Entonces el Coordinador recibe el resultado "PR-99: no solicitada: práctica no encontrada"
    Y no se registra ningún ActaFinal

  Escenario: Excepción - un usuario sin el rol CoordinadorPracticas solicita actas (ADR-004, ADR-006)
    Dado el Tutor "T-400" autenticado por el SSO con el rol Tutor
    Cuando el Tutor "T-400" solicita las actas de la Practica "PR-08"
    Entonces la petición se rechaza con el error de aplicación "acceso denegado"
    Y no se registra ningún ActaFinal
    Y la bitácora de auditoría tiene un registro del acceso rechazado con usuario "T-400", rol "Tutor", recurso la Practica "PR-08", acción "solicitar acta" y la hora

  Escenario: Excepción - petición con token vencido (ADR-004)
    Dado una solicitud de actas con un token emitido hace 16 minutos
    Cuando la API recibe la petición
    Entonces la petición se rechaza por falta de autenticación
    Y no se registra ningún ActaFinal

  Escenario: Flujo alterno - la generación falla una vez y se reintenta después de 1 minuto (ADR-001)
    Dado que el acta de la Practica "PR-08" está en la cola "actas"
    Y que el repositorio de actas no está disponible para el primer intento
    Cuando el Worker de actas procesa la cola
    Entonces se registra el IntentoGeneracion 1 con resultado "fallido: repositorio de actas no disponible"
    Y la SolicitudActa vuelve a la cola "actas" con el intento 2, disponible 1 minuto después
    Y si el Worker procesa la cola antes de ese minuto, no la toma
    Y cuando el Worker procesa la cola pasado el minuto, el IntentoGeneracion 2 es "exitoso" y el acta queda "generada"

  Escenario: Excepción - la generación falla 3 veces y el acta pasa a la cola de errores (ADR-001, DT-01)
    Dado que el acta de la Practica "PR-08" está en la cola "actas"
    Y que el repositorio de actas no está disponible para tres intentos
    Cuando el Worker de actas procesa la cola, después de 1 minuto y después de otros 2 minutos
    Entonces hay 3 IntentoGeneracion "fallido" del acta
    Y la SolicitudActa queda en la cola "errores_actas" y la cola "actas" queda vacía
    Y el ActaFinal queda en estado "con error"
    Y la bitácora de auditoría tiene un registro de usuario "worker-actas" con la acción "cambiar estado de en generación a con error"

  Escenario: Flujo alterno - el correo de aviso falla (ADR-007)
    Dado que el acta de la Practica "PR-08" está en la cola "actas"
    Y que el Servicio de correo institucional no está disponible
    Cuando el Worker de actas procesa la cola
    Entonces el ActaFinal queda en estado "generada"
    Y el aviso queda registrado como pendiente de reenvío

  Escenario: EAC-02 - 500 actas en el cierre, con fallas, sin perder ninguna
    Dado 500 Practicas en estado "evaluada"
    Y que el repositorio de actas falla en 30 intentos de guardado
    Cuando el Coordinador solicita las 500 actas a la vez y el Worker de actas procesa la cola hasta vaciarla
    Entonces la solicitud se acepta en menos de 3 segundos
    Y hay 500 ActaFinal: 0 actas perdidas
    Y el 100% de las actas termina "generada" o en la cola "errores_actas"
    Y el 95% o más de las actas queda "generada" en 10 minutos o menos después de solicitada

  Escenario: Flujo alterno - falla la composición del PDF y se reintenta (ADR-001, ADR-011)
    Dado que el acta de la Practica "PR-08" está en la cola "actas"
    Y que el componedor del PDF falla en el primer intento
    Cuando el Worker de actas procesa la cola y la vuelve a procesar 1 minuto después
    Entonces el IntentoGeneracion 1 es "fallido: no se pudo componer el PDF del acta"
    Y el IntentoGeneracion 2 es "exitoso" y el acta queda "generada"
