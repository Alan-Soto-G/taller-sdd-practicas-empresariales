# language: es
# Traza: CU-13, PA-07, S-04, ADR-002, ADR-004, ADR-006, ADR-007, ADR-008, ADR-012
# EAC: ningún EAC cita a CU-13. docs/drivers.md: "operación de una sola vez al arrancar (S-04); se resuelve
#      como preocupación PA-07" (cuadrante "cuestionar").
# Fuentes: ADR-008 ("un importador de una sola vez (CU-13) que valida los archivos de Excel y reporta las
#          filas rechazadas, sin cargarlas en silencio"), PA-07 (cargar empresas, plazas, tutores y prácticas
#          en curso), vista de desarrollo (Módulo Configuración: "importador de Excel de CU-13"), vista lógica
#          (Empresa, Plaza, Tutor, Estudiante, Practica), CU-02 (reglas de la Plaza).
#
# Decisiones de la revisión (se eligió la opción más simple, coherente con los ADR y con CU-01 a CU-12):
# - El Coordinador sube el archivo .xlsx tal como lo tiene. Lo lee openpyxl detrás del puerto LectorExcel
#   (ADR-012, 2026-11-20, aprobado por el usuario). Un archivo que no es un .xlsx válido responde 422 "archivo
#   no válido" con el motivo "el archivo no es un Excel .xlsx válido" y no carga nada. La primera versión de
#   esta spec recibía el libro ya leído; ese camino se conserva (mismas reglas) para quien ya tenga las filas.
# - Las celdas se leen como texto: un número entero (por ejemplo 3, que Excel guarda como 3.0) se lee "3", y
#   una celda vacía se lee vacía. Las filas vacías del final de la hoja se ignoran.
# - Hojas y columnas: "Empresas" (id, razon_social), "Plazas" (id, id_empresa, cargo, cupos, periodo),
#   "Tutores" (id, correo), "Estudiantes" (id, correo) y "Practicas" (id, id_estudiante, id_empresa,
#   id_tutor). Se procesan en ese orden, para que una fila pueda referirse a lo cargado en una hoja anterior.
# - Cada fila se valida con las reglas del dominio; las válidas se cargan y cada rechazada se reporta con su
#   hoja, su número de fila en el Excel (la fila 1 es el encabezado) y el motivo (ADR-008). Una hoja
#   desconocida se reporta como rechazada con la fila 1.
# - Motivos: "falta el campo <campo>", "ya existe <entidad> <id>", "la empresa <id> no existe", "el
#   estudiante <id> no existe", "el tutor <id> no existe", "los cupos deben ser un número entero", "el
#   correo no es válido" y los motivos de la Plaza de CU-02.
# - Las prácticas importadas son prácticas en curso (PA-07): quedan "en curso", con la versión de
#   ReglaPractica vigente (ADR-008).
# - Solo el rol CoordinadorPracticas importa. Otro rol recibe "acceso denegado" y se audita (ADR-004,
#   ADR-006). Se audita la creación de cada Práctica importada ("crear con estado en curso por importación") y
#   un resumen de la importación.
# - Importar de nuevo el mismo libro no duplica datos: las filas ya cargadas se rechazan como existentes.
Característica: Cargar información histórica desde Excel
  Como Coordinador de Prácticas autenticado por el SSO institucional
  quiero cargar las empresas, plazas, tutores, estudiantes y prácticas en curso de los Excel actuales
  para arrancar el sistema con la información vigente sin digitarla a mano (S-04, PA-07)

  Antecedentes:
    Dado la ReglaPractica vigente "v1"
    Y la Empresa "EMP-ACME" ya registrada
    Y el Coordinador "C-01" autenticado por el SSO con el rol CoordinadorPracticas

  Escenario: Flujo básico - se importa un libro válido
    Dado un libro con la Empresa "EMP-H1", la Plaza "PL-H1" de "EMP-H1" (cargo "Analista", 3 cupos, periodo "2026-2"), el Tutor "T-H1", el Estudiante "E-H1" y la Practica "PR-H1" de "E-H1" en "EMP-H1" con el Tutor "T-H1"
    Cuando el Coordinador "C-01" importa el libro
    Entonces se cargan 1 empresa, 1 plaza, 1 tutor, 1 estudiante y 1 práctica, y no hay filas rechazadas
    Y la Practica "PR-H1" queda "en curso" con el Tutor "T-H1" y la regla "v1"
    Y la bitácora de auditoría tiene la creación de "PR-H1" y el resumen de la importación, con usuario "C-01"

  Escenario: Flujo alterno - las filas inválidas se reportan y las válidas se cargan (ADR-008)
    Dado un libro con estas filas, además de las válidas del flujo básico:
      | hoja        | fila | datos                                         | motivo                                   |
      | Empresas    | 3    | id "EMP-ACME"                                 | ya existe empresa EMP-ACME               |
      | Empresas    | 4    | id "EMP-H2" sin razón social                  | falta el campo razon_social              |
      | Plazas      | 3    | empresa "EMP-99"                              | la empresa EMP-99 no existe              |
      | Plazas      | 4    | cupos "tres"                                  | los cupos deben ser un número entero     |
      | Plazas      | 5    | cupos 0                                       | los cupos deben ser mayores que cero     |
      | Tutores     | 3    | correo "sin-arroba"                           | el correo no es válido                   |
      | Practicas   | 3    | estudiante "E-99"                             | el estudiante E-99 no existe             |
      | Practicas   | 4    | tutor "T-99"                                  | el tutor T-99 no existe                  |
    Cuando el Coordinador "C-01" importa el libro
    Entonces se cargan las filas válidas: 1 empresa, 1 plaza, 1 tutor, 1 estudiante y 1 práctica
    Y se reportan las 8 filas rechazadas con su hoja, su fila y su motivo
    Y ninguna fila rechazada queda cargada

  Escenario: Flujo alterno - importar dos veces el mismo libro no duplica datos
    Dado que el Coordinador ya importó el libro del flujo básico
    Cuando el Coordinador "C-01" importa otra vez el mismo libro
    Entonces se cargan 0 filas y se rechazan 5, cada una con el motivo "ya existe <entidad> <id>"

  Escenario: Excepción - el libro tiene una hoja desconocida
    Dado un libro con la hoja "Notas"
    Cuando el Coordinador "C-01" importa el libro
    Entonces se reporta la hoja "Notas", fila 1, con el motivo "hoja desconocida"

  Escenario: Excepción - un usuario sin el rol CoordinadorPracticas importa (ADR-004, ADR-006)
    Dado el Tutor "T-500" autenticado por el SSO con el rol Tutor
    Cuando el Tutor "T-500" importa el libro del flujo básico
    Entonces la petición se rechaza con el error de aplicación "acceso denegado"
    Y no se carga ningún dato
    Y la bitácora de auditoría tiene un registro del acceso rechazado con usuario "T-500", rol "Tutor", recurso "importacion", acción "importar histórico" y la hora

  Escenario: Excepción - petición con token vencido (ADR-004)
    Dado una importación con un token emitido hace 16 minutos
    Cuando la API recibe la petición
    Entonces la petición se rechaza por falta de autenticación

  Escenario: Flujo alterno - el Coordinador sube el archivo .xlsx (ADR-012)
    Dado un archivo .xlsx con las hojas y las filas del flujo alterno de filas inválidas
    Cuando el Coordinador "C-01" sube el archivo para importarlo
    Entonces se cargan las mismas filas válidas y se reportan las mismas 8 filas rechazadas, con su hoja, su fila y su motivo

  Escenario: Excepción - el archivo no es un Excel válido (ADR-007, ADR-012)
    Dado un archivo que no es un .xlsx
    Cuando el Coordinador "C-01" sube el archivo para importarlo
    Entonces la petición se rechaza con el error de aplicación "archivo no válido" y el motivo "el archivo no es un Excel .xlsx válido"
    Y no se carga ningún dato

  Escenario: Excepción - un usuario sin el rol CoordinadorPracticas sube el archivo (ADR-004, ADR-006)
    Cuando el Tutor "T-500" sube el archivo .xlsx del flujo básico
    Entonces la petición se rechaza con el error de aplicación "acceso denegado" antes de leer el archivo
    Y la bitácora de auditoría tiene un registro del acceso rechazado con recurso "importacion" y acción "importar histórico"
