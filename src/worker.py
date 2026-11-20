"""Composicion del Worker de actas: otro proceso que reutiliza dominio, el caso de uso GenerarActa y los adaptadores; la API nunca compone el acta (ADR-001, ADR-002, ADR-011). En esta etapa recibe los mismos adaptadores en memoria que la API, en lugar de PostgreSQL y RabbitMQ."""

from collections.abc import Callable
from datetime import datetime

from aplicacion.actas.generar_acta import GenerarActa
from infraestructura.almacen_actas_memoria import AlmacenActasMemoria
from infraestructura.bitacora_memoria import BitacoraMemoria
from infraestructura.cola_actas_memoria import ColaActasMemoria
from infraestructura.componedor_acta_reportlab import ComponedorActaReportlab
from infraestructura.notificador_simulado import NotificadorSimulado
from infraestructura.repositorio_practicas_memoria import RepositorioPracticasMemoria
from infraestructura.worker_actas import WorkerActas


def construir_worker(
    repositorio: RepositorioPracticasMemoria,
    bitacora: BitacoraMemoria,
    notificador: NotificadorSimulado,
    cola: ColaActasMemoria,
    almacen: AlmacenActasMemoria,
    reloj: Callable[[], datetime] = datetime.now,
) -> WorkerActas:
    generar_acta = GenerarActa(
        repositorio,
        bitacora,
        almacen,
        ComponedorActaReportlab(),
        notificador,
        reloj=reloj,
    )
    return WorkerActas(cola, generar_acta)


def main() -> None:
    from main import construir

    app = construir()
    worker = construir_worker(
        app["repositorio"],
        app["bitacora"],
        app["notificador"],
        app["cola_actas"],
        app["almacen_actas"],
    )
    print(app["controlador"].solicitar_actas("tok-C-01", {"ids_practicas": ["PR-08"]}))
    print("procesadas:", worker.procesar(datetime.now()))
    print(app["repositorio"].listar_actas())


if __name__ == "__main__":
    main()
