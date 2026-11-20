# language: es
# Traza: CU-02, ADR-002, ADR-004, ADR-006, ADR-007
# EAC: ningún EAC de docs/drivers.md cita a CU-02 en su traza (EAC-04 cita CU-04, CU-05 y CU-10).
#      El rechazo auditado de roles no autorizados sale de ADR-004 y ADR-006, no de un EAC.
# Fuentes: docs/drivers.md (CU-02: "CRUD estándar sobre empresas ya aliadas"), vista lógica
#          (Plaza: cargo, cupos, periodo; "no admite más postulaciones aceptadas que cupos"),
#          glosario (Plaza: vacante que ofrece una empresa, con sus cupos).
#
# Decisiones de la revisión (se eligió la opción más simple, coherente con los ADR y con CU-01):
# - Alcance: CU-02 cubre solo publicar (crear) una Plaza. Editar, cerrar o eliminar plazas queda fuera.
# - Datos de la Plaza: Empresa, cargo, cupos y periodo (vista lógica y entidad Plaza de CU-01); no hay más
#   datos obligatorios.
# - Cupos: entero mayor que cero; no hay máximo.
# - Periodo: formato "AAAA-1" o "AAAA-2" (como "2026-2" en CU-01). No se valida si el periodo ya terminó,
#   igual que CU-01 no tiene ventana de fechas.
# - Se permiten varias Plazas con la misma Empresa, cargo y periodo: no hay control de duplicados.
# - Toda Empresa registrada es aliada con convenio vigente (alcance de la visión); no se valida el convenio,
#   solo que la Empresa exista.
# - La bitácora registra los cambios de estado de las entidades que lista ADR-006 y los accesos rechazados.
#   La Plaza no está en esa lista y no tiene estados, así que publicarla no se audita; los rechazos por
#   validación tampoco (igual que en CU-01).
# - La Empresa usa el id "EMP-ACME", el mismo que la Plaza "PL-01" precargada por CU-01 en main.py.
# - La carpeta es specs/002-publicar-plaza-practica/; el enlace de docs/drivers.md se corrige a esta carpeta.
Característica: Publicar plazas de práctica
  Como Coordinador de Prácticas autenticado por el SSO institucional
  quiero publicar las plazas de práctica que ofrecen las empresas aliadas, con su cargo, cupos y periodo
  para que los estudiantes puedan postularse a ellas (CU-01)

  Antecedentes:
    Dado la Empresa "EMP-ACME" "Acme S.A.S." aliada con convenio vigente
    Y el Coordinador de Prácticas "C-01" autenticado por el SSO con el rol CoordinadorPracticas

  Escenario: Flujo básico - el Coordinador publica una plaza
    Cuando el Coordinador "C-01" publica una Plaza de la Empresa "EMP-ACME" con cargo "Practicante de desarrollo", 2 cupos y periodo "2026-2"
    Entonces se registra una Plaza de la Empresa "EMP-ACME" con cargo "Practicante de desarrollo", 2 cupos y periodo "2026-2"
    Y el Coordinador recibe la confirmación "plaza publicada" con el identificador de la Plaza
    Y la bitácora de auditoría no tiene registros nuevos

  Escenario: Flujo alterno - un Estudiante se postula a la plaza recién publicada (CU-01)
    Dado que el Coordinador "C-01" publicó una Plaza de la Empresa "EMP-ACME" con cargo "Practicante de desarrollo", 2 cupos y periodo "2026-2"
    Y el Estudiante "E-1001" autenticado por el SSO con el rol Estudiante, sin postulaciones
    Cuando el Estudiante "E-1001" se postula a esa Plaza
    Entonces se registra una Postulacion del Estudiante "E-1001" a esa Plaza con estado "enviada"

  Escenario: Flujo alterno - se publica otra plaza igual de la misma empresa en el mismo periodo
    Dado que existe la Plaza "PL-01" de la Empresa "EMP-ACME" con cargo "Practicante de desarrollo", 2 cupos y periodo "2026-2"
    Cuando el Coordinador "C-01" publica una Plaza de la Empresa "EMP-ACME" con cargo "Practicante de desarrollo", 1 cupo y periodo "2026-2"
    Entonces se registra una nueva Plaza con un identificador distinto de "PL-01"
    Y la Empresa "EMP-ACME" tiene 2 Plazas en el periodo "2026-2"

  Escenario: Excepción - la empresa no existe
    Cuando el Coordinador "C-01" publica una Plaza de la Empresa "EMP-99", que no existe, con cargo "Practicante", 1 cupo y periodo "2026-2"
    Entonces la publicación se rechaza con el error de aplicación "empresa no encontrada"
    Y no se registra ninguna Plaza

  Esquema del escenario: Excepción - los datos de la plaza no son válidos
    Cuando el Coordinador "C-01" publica una Plaza de la Empresa "EMP-ACME" con cargo "<cargo>", <cupos> cupos y periodo "<periodo>"
    Entonces la publicación se rechaza con el error de aplicación "plaza no válida" y el motivo "<motivo>"
    Y no se registra ninguna Plaza

    Ejemplos:
      | cargo       | cupos | periodo | motivo                                 |
      | Practicante | 0     | 2026-2  | los cupos deben ser mayores que cero   |
      | Practicante | -1    | 2026-2  | los cupos deben ser mayores que cero   |
      |             | 2     | 2026-2  | el cargo es obligatorio                |
      | Practicante | 2     | 2026-3  | el periodo debe tener el formato AAAA-1 o AAAA-2 |
      | Practicante | 2     | 2026    | el periodo debe tener el formato AAAA-1 o AAAA-2 |

  Escenario: Excepción - un usuario sin el rol CoordinadorPracticas intenta publicar una plaza (ADR-004, ADR-006)
    Dado el Estudiante "E-1001" autenticado por el SSO con el rol Estudiante
    Cuando el Estudiante "E-1001" intenta publicar una Plaza de la Empresa "EMP-ACME" con cargo "Practicante", 1 cupo y periodo "2026-2"
    Entonces la petición se rechaza con el error de aplicación "acceso denegado"
    Y no se registra ninguna Plaza
    Y la bitácora de auditoría tiene un registro del acceso rechazado con usuario "E-1001", rol "Estudiante", recurso la Empresa "EMP-ACME", acción "publicar plaza" y la hora

  Escenario: Excepción - petición con token vencido (ADR-004)
    Dado una petición de publicación de Plaza con un token emitido hace 16 minutos
    Cuando la API recibe la petición
    Entonces la petición se rechaza por falta de autenticación
    Y no se registra ninguna Plaza
