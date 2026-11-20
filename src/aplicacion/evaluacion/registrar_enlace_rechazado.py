"""Caso de uso: audita cada intento con un enlace vencido, usado o invalido; los casos de uso escriben en la Bitacora, no los adaptadores (ADR-005, ADR-006)."""

from collections.abc import Callable
from datetime import datetime

from aplicacion.evaluacion.intento_enlace_rechazado import IntentoEnlaceRechazado
from aplicacion.puertos.bitacora import Bitacora

ROL_REPRESENTANTE = "RepresentanteEmpresa"


class RegistrarEnlaceRechazado:
    """Registra en la bitacora el intento rechazado con usuario, recurso, accion y hora."""

    def __init__(self, bitacora: Bitacora, reloj: Callable[[], datetime] = datetime.now) -> None:
        self._bitacora = bitacora
        self._reloj = reloj

    def ejecutar(self, intento: IntentoEnlaceRechazado) -> None:
        """Audita el intento; si el enlace no existe, el usuario y el recurso quedan como desconocidos."""
        self._bitacora.registrar(
            intento.id_representante or "desconocido",
            ROL_REPRESENTANTE,
            f"enlace:{intento.id_enlace or 'desconocido'}",
            f"usar enlace rechazado: {intento.motivo}",
            self._reloj(),
        )
