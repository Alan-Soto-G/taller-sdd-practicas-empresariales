"""Adaptador de entrada del Worker de actas: consume la cola actas, ejecuta GenerarActa y reencola o manda a errores_actas segun el resultado (ADR-001)."""

from datetime import datetime

from aplicacion.actas.generar_acta import GenerarActa
from aplicacion.actas.solicitud_acta import SolicitudActa
from infraestructura.cola_actas_memoria import ColaActasMemoria


class WorkerActas:
    """Entrega cada SolicitudActa disponible al caso de uso de generacion."""

    def __init__(self, cola: ColaActasMemoria, generar_acta: GenerarActa) -> None:
        self._cola = cola
        self._generar_acta = generar_acta

    def procesar(self, ahora: datetime) -> int:
        """Procesa las solicitudes disponibles a esa hora y devuelve cuantas proceso."""
        procesadas = 0
        while (solicitud := self._cola.tomar(ahora)) is not None:
            resultado = self._generar_acta.ejecutar(solicitud)
            if resultado.estado == "reintentar":
                siguiente = SolicitudActa(solicitud.id_acta, solicitud.id_practica, solicitud.intento + 1)
                self._cola.reencolar(siguiente, ahora + resultado.espera)
            elif resultado.estado == "con error":
                self._cola.enviar_a_errores(solicitud)
            procesadas += 1
        return procesadas
