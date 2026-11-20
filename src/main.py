"""Composicion de CU-01 a CU-04: conecta dominio, aplicacion e infraestructura con adaptadores en memoria y carga los datos de los Antecedentes de specs/001 a specs/004."""

from datetime import datetime, timedelta

from dominio.empresa import Empresa
from dominio.estado_practica import EstadoPractica
from dominio.estudiante import Estudiante
from dominio.plaza import Plaza
from dominio.practica import Practica
from dominio.regla_practica import ReglaPractica
from dominio.tutor import Tutor
from infraestructura.notificador_simulado import NotificadorSimulado
from infraestructura.repositorio_practicas_memoria import RepositorioPracticasMemoria
from infraestructura.bitacora_memoria import BitacoraMemoria
from infraestructura.proveedor_identidad_simulado import ProveedorIdentidadSimulado
from infraestructura.validador_token import ValidadorToken
from aplicacion.asignacion.asignar_tutor import AsignarTutor
from aplicacion.configuracion.consultar_regla_vigente import ConsultarReglaVigente
from aplicacion.horas.registrar_horas import RegistrarHoras
from aplicacion.postulaciones.postularse_plaza import PostularsePlaza
from aplicacion.postulaciones.publicar_plaza import PublicarPlaza
from infraestructura.controlador_rest import ControladorRest


def construir() -> dict[str, object]:
    repositorio = RepositorioPracticasMemoria()
    bitacora = BitacoraMemoria()
    notificador = NotificadorSimulado()
    proveedor = ProveedorIdentidadSimulado(reloj=datetime.now)
    validador = ValidadorToken(proveedor)
    caso_de_uso = PostularsePlaza(repositorio, bitacora, reloj=datetime.now)
    publicar_plaza = PublicarPlaza(repositorio, bitacora, reloj=datetime.now)
    consultar_regla = ConsultarReglaVigente(repositorio)
    asignar_tutor = AsignarTutor(
        repositorio,
        bitacora,
        notificador,
        consultar_regla,
        reloj=datetime.now,
    )
    registrar_horas = RegistrarHoras(repositorio, bitacora, reloj=datetime.now)
    controlador = ControladorRest(
        validador,
        caso_de_uso,
        publicar_plaza,
        asignar_tutor,
        registrar_horas,
    )

    repositorio.agregar_empresa(Empresa("EMP-ACME", "Acme S.A.S."))
    repositorio.agregar_plaza(
        Plaza("PL-01", "EMP-ACME", "Practicante de desarrollo", 2, "2026-2")
    )

    # Antecedentes de specs/003 (CU-03)
    repositorio.agregar_regla(
        ReglaPractica("v1", 160, 2, "plantilla-acta-v1")
    )
    repositorio.agregar_tutor(Tutor("T-200", "t200@universidad.edu.co"))
    repositorio.agregar_tutor(Tutor("T-300", "t300@universidad.edu.co"))
    repositorio.agregar_estudiante(
        Estudiante("E-1001", "e1001@universidad.edu.co")
    )
    repositorio.agregar_estudiante(
        Estudiante("E-1002", "e1002@universidad.edu.co")
    )
    repositorio.agregar_estudiante(
        Estudiante("E-1003", "e1003@universidad.edu.co")
    )
    repositorio.agregar_practica(
        Practica("PR-01", "E-1001", "EMP-ACME", "v1", EstadoPractica.SIN_TUTOR)
    )
    repositorio.agregar_practica(
        Practica("PR-02", "E-1002", "EMP-ACME", "v1", EstadoPractica.SIN_TUTOR)
    )
    repositorio.agregar_practica(
        Practica(
            "PR-03",
            "E-1003",
            "EMP-ACME",
            "v1",
            EstadoPractica.EN_CURSO,
            "T-300",
        )
    )

    # Antecedentes de specs/004 (CU-04)
    repositorio.agregar_estudiante(Estudiante("E-1004", "e1004@universidad.edu.co"))
    repositorio.agregar_practica(Practica("PR-04", "E-1004", "EMP-ACME", "v1", EstadoPractica.EN_CURSO, "T-300"))

    ahora = datetime.now()
    proveedor.emitir("tok-E-1001", "E-1001", "Estudiante", ahora)
    proveedor.emitir("tok-E-1002", "E-1002", "Estudiante", ahora)
    proveedor.emitir("tok-E-1004", "E-1004", "Estudiante", ahora)
    proveedor.emitir("tok-T-200", "T-200", "Tutor", ahora)
    proveedor.emitir("tok-T-300", "T-300", "Tutor", ahora)
    proveedor.emitir("tok-C-01", "C-01", "CoordinadorPracticas", ahora)
    proveedor.emitir(
        "tok-vencido",
        "E-1001",
        "Estudiante",
        ahora - timedelta(minutes=16),
    )

    return {
        "repositorio": repositorio,
        "bitacora": bitacora,
        "proveedor": proveedor,
        "controlador": controlador,
        "publicar_plaza": publicar_plaza,
        "notificador": notificador,
        "asignar_tutor": asignar_tutor,
        "registrar_horas": registrar_horas,
    }


def main() -> None:
    app = construir()
    controlador = app["controlador"]
    bitacora = app["bitacora"]

    estado_http, cuerpo = controlador.postular(
        "tok-E-1001",
        {"id_plaza": "PL-01"},
    )
    print(estado_http)
    print(cuerpo)

    for registro in bitacora.listar():
        print(registro)


if __name__ == "__main__":
    main()
