"""Composicion de la API para CU-01 a CU-07: conecta dominio, aplicacion e infraestructura con adaptadores en memoria y carga los datos de los Antecedentes de specs/001 a specs/007. El Worker de actas tiene su propia composicion en worker.py (ADR-001, ADR-002)."""

from datetime import date, datetime, timedelta

from dominio.coordinador_practicas import CoordinadorPracticas
from dominio.criterio_evaluacion import CriterioEvaluacion
from dominio.empresa import Empresa
from dominio.estado_practica import EstadoPractica
from dominio.estado_registro_horas import EstadoRegistroHoras
from dominio.estudiante import Estudiante
from dominio.evaluacion import Evaluacion
from dominio.plaza import Plaza
from dominio.practica import Practica
from dominio.representante_empresa import RepresentanteEmpresa
from dominio.regla_practica import ReglaPractica
from dominio.registro_horas import RegistroHoras
from dominio.tutor import Tutor
from infraestructura.almacen_actas_memoria import AlmacenActasMemoria
from infraestructura.cola_actas_memoria import ColaActasMemoria
from infraestructura.validador_enlace import ValidadorEnlace
from infraestructura.notificador_simulado import NotificadorSimulado
from infraestructura.repositorio_practicas_memoria import RepositorioPracticasMemoria
from infraestructura.bitacora_memoria import BitacoraMemoria
from infraestructura.proveedor_identidad_simulado import ProveedorIdentidadSimulado
from infraestructura.validador_token import ValidadorToken
from aplicacion.actas.solicitar_actas import SolicitarActas
from aplicacion.asignacion.asignar_tutor import AsignarTutor
from aplicacion.configuracion.consultar_criterios_evaluacion import ConsultarCriteriosEvaluacion
from aplicacion.configuracion.consultar_horas_requeridas import ConsultarHorasRequeridas
from aplicacion.configuracion.consultar_regla_vigente import ConsultarReglaVigente
from aplicacion.evaluacion.emitir_enlace_evaluacion import EmitirEnlaceEvaluacion
from aplicacion.evaluacion.consultar_formulario_evaluacion import ConsultarFormularioEvaluacion
from aplicacion.evaluacion.registrar_evaluacion import RegistrarEvaluacion
from aplicacion.horas.aprobar_horas import AprobarHoras
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
    consultar_horas = ConsultarHorasRequeridas(repositorio)
    aprobar_horas = AprobarHoras(
        repositorio, bitacora, consultar_horas, reloj=datetime.now
    )
    validador_enlace = ValidadorEnlace(repositorio, bitacora, reloj=datetime.now)
    consultar_criterios = ConsultarCriteriosEvaluacion(repositorio)
    emitir_enlace_evaluacion = EmitirEnlaceEvaluacion(
        repositorio, bitacora, notificador, reloj=datetime.now
    )
    consultar_formulario_evaluacion = ConsultarFormularioEvaluacion(
        repositorio, consultar_criterios
    )
    registrar_evaluacion = RegistrarEvaluacion(
        repositorio, bitacora, consultar_criterios, reloj=datetime.now
    )
    cola_actas = ColaActasMemoria(reloj=datetime.now)
    almacen_actas = AlmacenActasMemoria()
    solicitar_actas = SolicitarActas(
        repositorio, bitacora, cola_actas, reloj=datetime.now
    )
    controlador = ControladorRest(
        validador,
        caso_de_uso,
        publicar_plaza,
        asignar_tutor,
        registrar_horas,
        aprobar_horas,
        validador_enlace,
        emitir_enlace_evaluacion,
        consultar_formulario_evaluacion,
        registrar_evaluacion,
        solicitar_actas,
    )

    repositorio.agregar_empresa(Empresa("EMP-ACME", "Acme S.A.S."))
    repositorio.agregar_plaza(
        Plaza("PL-01", "EMP-ACME", "Practicante de desarrollo", 2, "2026-2")
    )

    # Antecedentes de specs/003 (CU-03)
    repositorio.agregar_regla(
        ReglaPractica(
            "v1",
            160,
            2,
            "plantilla-acta-v1",
            (
                CriterioEvaluacion("Responsabilidad", 5),
                CriterioEvaluacion("Trabajo en equipo", 5),
                CriterioEvaluacion("Calidad técnica", 5),
            ),
        )
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

    # Antecedentes de specs/005 (CU-05)
    repositorio.agregar_estudiante(Estudiante("E-1005", "e1005@universidad.edu.co"))
    repositorio.agregar_practica(Practica("PR-05", "E-1005", "EMP-ACME", "v1", EstadoPractica.EN_CURSO, "T-300"))
    repositorio.guardar_registro_horas(RegistroHoras.reportar("RH-05", "PR-05", "2026-W46", 20, "Desarrollo de la API", date(2026, 11, 13)))

    # Antecedentes de specs/006 (CU-06)
    repositorio.agregar_representante(RepresentanteEmpresa("R-01", "EMP-ACME", "Representante de Acme", "representante@acme.example"))
    repositorio.agregar_tutor(Tutor("T-400", "t400@universidad.edu.co"))
    repositorio.agregar_estudiante(Estudiante("E-1006", "e1006@universidad.edu.co"))
    repositorio.agregar_practica(Practica("PR-06", "E-1006", "EMP-ACME", "v1", EstadoPractica.HORAS_COMPLETAS, "T-400"))

    # Antecedentes de specs/007 (CU-07)
    repositorio.agregar_coordinador(CoordinadorPracticas("C-01", "coordinacion@universidad.edu.co"))
    repositorio.agregar_estudiante(Estudiante("E-1008", "e1008@universidad.edu.co"))
    repositorio.agregar_practica(Practica("PR-08", "E-1008", "EMP-ACME", "v1", EstadoPractica.EVALUADA, "T-400"))
    for semana in range(30, 38):
        repositorio.guardar_registro_horas(RegistroHoras(f"RH-08-{semana}", "PR-08", f"2026-W{semana}", 20, "Desarrollo", date(2026, 8, 1), EstadoRegistroHoras.APROBADO))
    repositorio.guardar_evaluacion(Evaluacion("EV-08", "PR-08", {"Responsabilidad": 5, "Trabajo en equipo": 5, "Calidad técnica": 4}, "Cumplió los objetivos", date(2026, 11, 10)))

    ahora = datetime.now()
    proveedor.emitir("tok-E-1001", "E-1001", "Estudiante", ahora)
    proveedor.emitir("tok-E-1002", "E-1002", "Estudiante", ahora)
    proveedor.emitir("tok-E-1004", "E-1004", "Estudiante", ahora)
    proveedor.emitir("tok-E-1005", "E-1005", "Estudiante", ahora)
    proveedor.emitir("tok-T-200", "T-200", "Tutor", ahora)
    proveedor.emitir("tok-T-300", "T-300", "Tutor", ahora)
    proveedor.emitir("tok-T-400", "T-400", "Tutor", ahora)
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
        "aprobar_horas": aprobar_horas,
        "validador_enlace": validador_enlace,
        "emitir_enlace_evaluacion": emitir_enlace_evaluacion,
        "registrar_evaluacion": registrar_evaluacion,
        "cola_actas": cola_actas,
        "almacen_actas": almacen_actas,
        "solicitar_actas": solicitar_actas,
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
