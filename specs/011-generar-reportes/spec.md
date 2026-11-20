# language: es
# Traza: CU-11, OB-01, OB-02, OB-03, ADR-002, ADR-004, ADR-006, ADR-007
# EAC: ningún EAC cita a CU-11. docs/drivers.md: "importante para el negocio, pero no estructura nada: opera
#      sobre datos ya estructurados" (cuadrante "cuestionar" de la matriz de priorización).
# Fuentes: docs/drivers.md (CU-11, actor Coordinador de Prácticas), contexto (el Coordinador "genera
#          reportes"), vista de desarrollo (Módulo Seguimiento: CU-09 a CU-11; usa en solo lectura los
#          Módulos Horas y Actas), vista lógica (estados de Práctica y de ActaFinal).
#
# Decisiones de la revisión (se eligió la opción más simple, coherente con los ADR y con CU-01 a CU-10):
# - Un solo reporte, en JSON, con: total de prácticas; prácticas por estado (los 6 estados de la vista
#   lógica, con 0 si no hay); prácticas por empresa; prácticas por tutor ("sin tutor" si no tiene); actas
#   por estado (los 4 estados del acta más "sin acta"); y la suma de horas aprobadas. No se exporta a Excel
#   ni a PDF: ningún ADR aprueba una librería para reportes y el JSON lo puede mostrar la aplicación web.
# - El Coordinador puede filtrar el reporte por una Empresa. Una empresa inexistente responde
#   "empresa no encontrada" (error de CU-02).
# - Solo el rol CoordinadorPracticas genera reportes. Otro rol recibe "acceso denegado" y el intento se
#   audita con el recurso "reportes" y la acción "generar reporte" (ADR-004, ADR-006). Generar un reporte
#   no cambia estado y no se audita.
# - El reporte se calcula en el momento sobre los datos actuales (no se guarda).
# - Los datos son los ya precargados por CU-01 a CU-10; los valores esperados se calculan contando
#   directamente el repositorio en la validación.
Característica: Generar reportes de prácticas
  Como Coordinador de Prácticas autenticado por el SSO institucional
  quiero un reporte con el estado de todas las prácticas, sus actas y sus horas
  para seguir el proceso de la facultad sin consolidar hojas de Excel a mano (OB-01, OB-02, OB-03)

  Antecedentes:
    Dado las prácticas, horas y actas precargadas por CU-03 a CU-10
    Y el Coordinador "C-01" autenticado por el SSO con el rol CoordinadorPracticas

  Escenario: Flujo básico - el Coordinador genera el reporte general
    Cuando el Coordinador "C-01" genera el reporte de prácticas
    Entonces el total de prácticas es igual al número de prácticas del repositorio
    Y las prácticas por estado incluyen los 6 estados y suman el total
    Y las prácticas por empresa y por tutor suman el total
    Y las actas por estado incluyen "sin acta" y los 4 estados del acta, y suman el total
    Y la suma de horas aprobadas es igual a la suma de los registros aprobados
    Y la bitácora de auditoría no tiene registros nuevos

  Escenario: Flujo alterno - el reporte refleja los cambios del proceso
    Dado que el Coordinador solicitó el acta de la Practica "PR-08" y el Worker de actas la generó
    Cuando el Coordinador "C-01" genera el reporte de prácticas
    Entonces hay una práctica más en "acta en trámite" y una menos en "evaluada"
    Y hay un acta más en estado "generada" y una práctica menos "sin acta"

  Escenario: Flujo alterno - reporte filtrado por empresa
    Dado la Empresa "EMP-SIN" sin prácticas
    Cuando el Coordinador "C-01" genera el reporte de la Empresa "EMP-SIN"
    Entonces el total de prácticas es 0 y todos los conteos son 0

  Escenario: Excepción - la empresa del filtro no existe
    Cuando el Coordinador "C-01" genera el reporte de la Empresa "EMP-99", que no existe
    Entonces la petición se rechaza con el error de aplicación "empresa no encontrada"

  Escenario: Excepción - un usuario sin el rol CoordinadorPracticas genera el reporte (ADR-004, ADR-006)
    Dado el Tutor "T-500" autenticado por el SSO con el rol Tutor
    Cuando el Tutor "T-500" genera el reporte de prácticas
    Entonces la petición se rechaza con el error de aplicación "acceso denegado"
    Y la bitácora de auditoría tiene un registro del acceso rechazado con usuario "T-500", rol "Tutor", recurso "reportes", acción "generar reporte" y la hora

  Escenario: Excepción - petición con token vencido (ADR-004)
    Dado una petición de reporte con un token emitido hace 16 minutos
    Cuando la API recibe la petición
    Entonces la petición se rechaza por falta de autenticación
