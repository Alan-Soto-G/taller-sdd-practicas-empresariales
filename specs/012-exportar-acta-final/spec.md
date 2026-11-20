# language: es
# Traza: CU-12, EAC-04, OB-03, ADR-001, ADR-002, ADR-003, ADR-004, ADR-006, ADR-007, ADR-011
# EAC: ningún EAC cita a CU-12; el rechazo auditado del acceso ajeno sigue la medida de EAC-04 (ADR-004,
#      ADR-006). docs/drivers.md: "lectura de un archivo ya generado y almacenado".
# Fuentes: docs/drivers.md (CU-12, actores Coordinador de Prácticas o Estudiante), ADR-003 (el PDF está en el
#          Repositorio de actas; la API lo lee), vista de procesos (Repositorio de actas: "Worker de actas
#          escribe y API lee"), vista de desarrollo (Módulo Actas: CU-07, CU-08 y CU-12; Adaptador del
#          repositorio de actas: "lectura de PDF para exportar"), ADR-001 (la API nunca compone el PDF).
#
# Decisiones de la revisión (se eligió la opción más simple, coherente con los ADR y con CU-01 a CU-11):
# - Se exporta un ActaFinal "generada" o "aprobada": son las que tienen PDF. En "en generación" o
#   "con error" se responde 409 "exportación no permitida" con el motivo "el acta no tiene PDF generado".
# - La API solo lee el PDF ya guardado por el Worker (AlmacenActas.leer); nunca lo compone (ADR-001).
# - El Coordinador exporta cualquier acta; el Estudiante solo la de su práctica. Otro rol (incluido el
#   Tutor, que no es actor de CU-12) o un Estudiante ajeno recibe "acceso denegado" y el intento se audita
#   con la acción "exportar acta" (ADR-004, ADR-006). Exportar no cambia estado y no se audita.
# - La respuesta lleva el contenido del PDF, el tipo "application/pdf" y el nombre "acta-<id>.pdf".
# - Si el Repositorio de actas no responde o no tiene el archivo, el adaptador lo traduce a "repositorio de
#   actas no disponible" (error de CU-07) y se responde 503 (ADR-007).
# - Se usan el acta "AC-09" de "PR-09" (precargada por CU-08) y un acta de "PR-08" generada por el Worker
#   con ReportLab (CU-07, ADR-011) dentro de la validación.
Característica: Exportar el acta final
  Como Coordinador de Prácticas o como Estudiante titular de la práctica
  quiero descargar el PDF del acta final
  para archivarla o presentarla en los trámites de grado sin recolectar copias firmadas (OB-03)

  Antecedentes:
    Dado el ActaFinal "AC-09" de la Practica "PR-09" del Estudiante "E-1009" en estado "generada", con su PDF en el Repositorio de actas
    Y el Coordinador "C-01" y los Estudiantes "E-1009" y "E-1010" autenticados por el SSO

  Escenario: Flujo básico - el Coordinador exporta un acta generada por el Worker
    Dado que el Coordinador solicitó el acta de la Practica "PR-08" y el Worker de actas la generó con ReportLab
    Cuando el Coordinador "C-01" exporta esa acta
    Entonces recibe un archivo "application/pdf" llamado "acta-<id del acta>.pdf"
    Y el contenido es el PDF guardado por el Worker: empieza con "%PDF-" y termina con "%%EOF"
    Y la bitácora de auditoría no tiene registros nuevos

  Escenario: Flujo alterno - el Estudiante exporta el acta de su práctica
    Cuando el Estudiante "E-1009" exporta el ActaFinal "AC-09"
    Entonces recibe el archivo "acta-AC-09.pdf" con el contenido guardado en el Repositorio de actas

  Escenario: Flujo alterno - también se exporta un acta aprobada
    Dado que el ActaFinal "AC-09" tiene las tres aprobaciones y está "aprobada"
    Cuando el Coordinador "C-01" exporta el ActaFinal "AC-09"
    Entonces recibe el archivo "acta-AC-09.pdf"

  Esquema del escenario: Excepción - el acta no tiene PDF generado
    Dado el ActaFinal "AC-11" de la Practica "PR-09" en estado "<estado>"
    Cuando el Coordinador "C-01" exporta el ActaFinal "AC-11"
    Entonces la petición se rechaza con el error de aplicación "exportación no permitida" y el motivo "el acta no tiene PDF generado"

    Ejemplos:
      | estado        |
      | en generación |
      | con error     |

  Escenario: Excepción - el acta no existe
    Cuando el Coordinador "C-01" exporta el ActaFinal "AC-99", que no existe
    Entonces la petición se rechaza con el error de aplicación "acta no encontrada"

  Escenario: EAC-04 - un estudiante intenta exportar el acta de otro
    Cuando el Estudiante "E-1010" exporta el ActaFinal "AC-09", que es de "E-1009"
    Entonces la petición se rechaza con el error de aplicación "acceso denegado"
    Y la bitácora de auditoría tiene un registro del acceso rechazado con usuario "E-1010", rol "Estudiante", recurso el acta "AC-09", acción "exportar acta" y la hora

  Escenario: Excepción - un rol que no es actor de CU-12 intenta exportar (ADR-004, ADR-006)
    Dado el Tutor "T-400" autenticado por el SSO con el rol Tutor
    Cuando el Tutor "T-400" exporta el ActaFinal "AC-09"
    Entonces la petición se rechaza con el error de aplicación "acceso denegado"
    Y la bitácora de auditoría tiene un registro del acceso rechazado con usuario "T-400", rol "Tutor", recurso el acta "AC-09", acción "exportar acta" y la hora

  Escenario: Excepción - el Repositorio de actas no tiene el archivo (ADR-007)
    Dado el ActaFinal "AC-12" "generada" cuya ruta no existe en el Repositorio de actas
    Cuando el Coordinador "C-01" exporta el ActaFinal "AC-12"
    Entonces la petición se responde con 503 y el error de aplicación "repositorio de actas no disponible"

  Escenario: Excepción - petición con token vencido (ADR-004)
    Dado una exportación del ActaFinal "AC-09" con un token emitido hace 16 minutos
    Cuando la API recibe la petición
    Entonces la petición se rechaza por falta de autenticación
