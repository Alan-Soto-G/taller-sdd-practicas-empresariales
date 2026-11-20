"""Composicion de CU-01 y CU-02: conecta dominio, aplicacion e infraestructura con adaptadores en memoria y carga los datos de los Antecedentes de specs/001-postularse-plaza-practica/spec.md y specs/002-publicar-plaza-practica/spec.md."""

from datetime import datetime, timedelta

from dominio.empresa import Empresa
from dominio.plaza import Plaza
from infraestructura.repositorio_practicas_memoria import RepositorioPracticasMemoria
from infraestructura.bitacora_memoria import BitacoraMemoria
from infraestructura.proveedor_identidad_simulado import ProveedorIdentidadSimulado
from infraestructura.validador_token import ValidadorToken
from aplicacion.postulaciones.postularse_plaza import PostularsePlaza
from aplicacion.postulaciones.publicar_plaza import PublicarPlaza
from infraestructura.controlador_rest import ControladorRest


def construir() -> dict[str, object]:
    repositorio = RepositorioPracticasMemoria()
    bitacora = BitacoraMemoria()
    proveedor = ProveedorIdentidadSimulado(reloj=datetime.now)
    validador = ValidadorToken(proveedor)
    caso_de_uso = PostularsePlaza(repositorio, bitacora, reloj=datetime.now)
    publicar_plaza = PublicarPlaza(repositorio, bitacora, reloj=datetime.now)
    controlador = ControladorRest(validador, caso_de_uso, publicar_plaza)

    repositorio.agregar_empresa(Empresa("EMP-ACME", "Acme S.A.S."))
    repositorio.agregar_plaza(
        Plaza("PL-01", "EMP-ACME", "Practicante de desarrollo", 2, "2026-2")
    )

    ahora = datetime.now()
    proveedor.emitir("tok-E-1001", "E-1001", "Estudiante", ahora)
    proveedor.emitir("tok-E-1002", "E-1002", "Estudiante", ahora)
    proveedor.emitir("tok-T-200", "T-200", "Tutor", ahora)
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
