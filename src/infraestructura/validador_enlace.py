"""Adaptador de entrada: valida el enlace de un solo uso del Representante y entrega una identidad acotada a una practica y a una accion; audita cada intento rechazado (ADR-005, ADR-006)."""

from collections.abc import Callable
from datetime import datetime

from aplicacion.errores.enlace_no_valido import EnlaceNoValido
from aplicacion.identidad_enlace import IdentidadEnlace
from aplicacion.puertos.bitacora import Bitacora
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas

ROL_REPRESENTANTE = "RepresentanteEmpresa"


class ValidadorEnlace:
    """Valida enlaces de acceso del Representante de la Empresa."""

    def __init__(
        self,
        repositorio: RepositorioPracticas,
        bitacora: Bitacora,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._repositorio = repositorio
        self._bitacora = bitacora
        self._reloj = reloj

    def validar(self, token: str, accion: str) -> IdentidadEnlace:
        """Devuelve la identidad del enlace o lanza EnlaceNoValido tras auditar el intento."""
        ahora = self._reloj()
        enlace = self._repositorio.obtener_enlace_por_token(token)
        if enlace is None:
            self._rechazar("desconocido", "enlace:desconocido", "enlace inválido", ahora)
        motivo = enlace.motivo_rechazo(accion, ahora)
        if motivo is not None:
            self._rechazar(enlace.id_representante, f"enlace:{enlace.id}", motivo, ahora)
        return IdentidadEnlace(
            enlace.id,
            enlace.id_practica,
            enlace.id_representante,
            enlace.accion,
        )

    def _rechazar(self, usuario: str, recurso: str, motivo: str, ahora: datetime) -> None:
        """Audita el intento con un enlace vencido, usado o invalido y lo niega."""
        self._bitacora.registrar(
            usuario,
            ROL_REPRESENTANTE,
            recurso,
            f"usar enlace rechazado: {motivo}",
            ahora,
        )
        raise EnlaceNoValido(motivo)
