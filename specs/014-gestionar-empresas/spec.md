# language: es
# Traza: CU-14, PA-02, DT-04, ADR-002, ADR-004, ADR-005, ADR-006, ADR-007
# EAC: ningún EAC cita a CU-14. docs/drivers.md: "CRUD estándar; las empresas ya tienen convenio (fuera del
#      alcance de la visión)".
# Fuentes: docs/drivers.md (CU-14, actor Coordinador de Prácticas), vista lógica (Empresa: NIT, razón social;
#          RepresentanteEmpresa: nombre, correo; "solo se gestionan empresas ya aliadas"), vista de desarrollo
#          (Módulo Postulaciones: CU-01, CU-02 y CU-14), ADR-005 (riesgo: el correo del representante puede
#          estar desactualizado; "el Coordinador lo verifica al gestionar la empresa (CU-14) y puede reemitir
#          el enlace").
#
# Decisiones de la revisión (se eligió la opción más simple, coherente con los ADR y con CU-01 a CU-13):
# - CRUD de Empresa: crear, listar, actualizar (razón social y NIT) y eliminar. Toda empresa registrada es
#   aliada con convenio vigente (CU-01, CU-02): el convenio no se gestiona aquí.
# - El NIT se escribe con 9 dígitos, un guion y el dígito de verificación (por ejemplo "900123456-7"); no se
#   calcula el dígito. La razón social es obligatoria. El id de la empresa es obligatorio y único.
# - Solo se elimina una empresa sin plazas ni prácticas: así no quedan plazas o prácticas sin empresa. Si
#   tiene, 409 "empresa no permitida" con el motivo "la empresa tiene plazas o prácticas".
# - Cada empresa tiene un RepresentanteEmpresa (CU-06 y CU-08 envían los enlaces a ese correo). Registrarlo
#   de nuevo actualiza su nombre y su correo y conserva su id. El nombre es obligatorio y el correo debe ser
#   válido (regla Correo de CU-13).
# - Cambiar el correo no reemite los enlaces ya enviados: los enlaces nuevos (CU-06, CU-08) usan el correo
#   actualizado, y el Coordinador reemite si hace falta (ADR-005, DT-04).
# - Errores: datos inválidos → 400 "empresa no válida" con el motivo; id repetido o eliminación con plazas o
#   prácticas → 409 "empresa no permitida" con el motivo; empresa inexistente → 404 "empresa no encontrada".
# - Solo el rol CoordinadorPracticas gestiona empresas. Otro rol recibe "acceso denegado" y se audita con la
#   acción "gestionar empresas" (ADR-004, ADR-006). Los cambios de Empresa no se auditan: Empresa no está entre
#   las entidades con cambios de estado de ADR-006 (igual que la Plaza en CU-02).
Característica: Gestionar empresas aliadas y sus representantes
  Como Coordinador de Prácticas autenticado por el SSO institucional
  quiero registrar y mantener las empresas aliadas y el correo de su representante
  para publicar plazas (CU-02) y enviar los enlaces de evaluación y de aprobación al correo correcto (ADR-005)

  Antecedentes:
    Dado la Empresa "EMP-ACME" "Acme S.A.S." con plazas y prácticas, y su RepresentanteEmpresa "R-01" con correo "representante@acme.example"
    Y el Coordinador "C-01" autenticado por el SSO con el rol CoordinadorPracticas

  Escenario: Flujo básico - el Coordinador registra una empresa y su representante
    Cuando el Coordinador "C-01" crea la Empresa "EMP-NUEVA" con razón social "Nueva Ltda." y NIT "900123456-7"
    Y registra su representante "Ana Pérez" con correo "ana@nueva.example"
    Entonces la Empresa "EMP-NUEVA" queda registrada con esa razón social y ese NIT
    Y su RepresentanteEmpresa tiene el nombre "Ana Pérez" y el correo "ana@nueva.example"
    Y el Coordinador puede publicar una Plaza de "EMP-NUEVA" (CU-02)

  Escenario: Flujo alterno - el Coordinador lista las empresas con su representante
    Cuando el Coordinador "C-01" lista las empresas
    Entonces recibe "EMP-ACME" con su NIT y el representante "R-01" con correo "representante@acme.example"

  Escenario: Flujo alterno - el Coordinador actualiza la razón social y el NIT
    Cuando el Coordinador "C-01" actualiza la Empresa "EMP-ACME" con razón social "Acme Colombia S.A.S." y NIT "800765432-1"
    Entonces la Empresa "EMP-ACME" queda con esos datos y conserva sus plazas

  Escenario: Flujo alterno - el correo actualizado del representante recibe los enlaces nuevos (ADR-005)
    Cuando el Coordinador "C-01" registra el representante de "EMP-ACME" con el nombre "Representante de Acme" y el correo "nuevo@acme.example"
    Entonces el RepresentanteEmpresa conserva el id "R-01" y queda con el correo "nuevo@acme.example"
    Y el enlace de evaluación que el Coordinador emite después para la Practica "PR-06" se envía a "nuevo@acme.example"

  Escenario: Flujo alterno - se elimina una empresa sin plazas ni prácticas
    Dado la Empresa "EMP-NUEVA" sin plazas ni prácticas
    Cuando el Coordinador "C-01" elimina la Empresa "EMP-NUEVA"
    Entonces la Empresa "EMP-NUEVA" ya no está registrada

  Escenario: Excepción - no se elimina una empresa con plazas o prácticas
    Cuando el Coordinador "C-01" elimina la Empresa "EMP-ACME"
    Entonces la petición se rechaza con el error de aplicación "empresa no permitida" y el motivo "la empresa tiene plazas o prácticas"
    Y la Empresa "EMP-ACME" sigue registrada

  Escenario: Excepción - el id de la empresa ya existe
    Cuando el Coordinador "C-01" crea la Empresa "EMP-ACME" con razón social "Otra" y NIT "900123456-7"
    Entonces la petición se rechaza con el error de aplicación "empresa no permitida" y el motivo "ya existe empresa EMP-ACME"

  Esquema del escenario: Excepción - los datos no son válidos
    Cuando el Coordinador "C-01" <acción>
    Entonces la petición se rechaza con el error de aplicación "empresa no válida" y el motivo "<motivo>"

    Ejemplos:
      | acción                                                                              | motivo                                                       |
      | crea la Empresa "EMP-X" con razón social "" y NIT "900123456-7"                     | la razón social es obligatoria                               |
      | crea la Empresa "EMP-X" con razón social "X" y NIT "123"                            | el NIT debe tener 9 dígitos, un guion y el dígito de verificación |
      | registra el representante de "EMP-ACME" con nombre "" y correo "a@b.co"             | el nombre del representante es obligatorio                   |
      | registra el representante de "EMP-ACME" con nombre "Ana" y correo "sin-arroba"      | el correo no es válido                                       |

  Escenario: Excepción - la empresa no existe
    Cuando el Coordinador "C-01" actualiza la Empresa "EMP-99", que no existe
    Entonces la petición se rechaza con el error de aplicación "empresa no encontrada"

  Escenario: Excepción - un usuario sin el rol CoordinadorPracticas gestiona empresas (ADR-004, ADR-006)
    Dado el Tutor "T-500" autenticado por el SSO con el rol Tutor
    Cuando el Tutor "T-500" crea la Empresa "EMP-T" con razón social "T" y NIT "900123456-7"
    Entonces la petición se rechaza con el error de aplicación "acceso denegado"
    Y la bitácora de auditoría tiene un registro del acceso rechazado con usuario "T-500", rol "Tutor", recurso la Empresa "EMP-T", acción "gestionar empresas" y la hora

  Escenario: Excepción - petición con token vencido (ADR-004)
    Dado una petición de gestión de empresas con un token emitido hace 16 minutos
    Cuando la API recibe la petición
    Entonces la petición se rechaza por falta de autenticación
