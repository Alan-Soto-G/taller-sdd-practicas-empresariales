"""Adaptador de entrada: valida el enlace de un solo uso del Representante y entrega una identidad acotada a una practica y a una accion (ADR-005). No escribe en la bitacora: el intento rechazado lo audita un caso de uso (ADR-006)."""

from collections.abc import Callable
from datetime import datetime

from aplicacion.errores.enlace_no_valido import EnlaceNoValido
from aplicacion.identidad_enlace import IdentidadEnlace
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas


class ValidadorEnlace:
    """Valida enlaces de acceso del Representante de la Empresa."""

    def __init__(
        self,
        repositorio: RepositorioPracticas,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._repositorio = repositorio
        self._reloj = reloj

    def validar(self, token: str, accion: str) -> IdentidadEnlace:
        """Devuelve la identidad del enlace o lanza EnlaceNoValido con el enlace y el representante."""
        enlace = self._repositorio.obtener_enlace_por_token(token)
        if enlace is None:
            raise EnlaceNoValido("enlace inválido")
        motivo = enlace.motivo_rechazo(accion, self._reloj())
        if motivo is not None:
            raise EnlaceNoValido(motivo, enlace.id, enlace.id_representante)
        return IdentidadEnlace(
            enlace.id,
            enlace.id_practica,
            enlace.id_representante,
            enlace.accion,
        )
