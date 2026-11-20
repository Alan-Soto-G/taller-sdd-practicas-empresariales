"""Caso de uso CU-12: el Coordinador o el Estudiante titular exportan el PDF del acta; la API solo lo lee del Repositorio de actas (ADR-001, ADR-003, ADR-004, ADR-006, ADR-007)."""

from collections.abc import Callable
from datetime import datetime

from aplicacion.actas.acta_exportada import ActaExportada
from aplicacion.actas.solicitud_exportacion_acta import SolicitudExportacionActa
from aplicacion.errores.acceso_denegado import AccesoDenegado
from aplicacion.errores.acta_no_encontrada import ActaNoEncontrada
from aplicacion.errores.acta_no_exportable import ActaNoExportable
from aplicacion.puertos.almacen_actas import AlmacenActas
from aplicacion.puertos.bitacora import Bitacora
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas
from dominio.estado_acta import EstadoActa

ROL_COORDINADOR = "CoordinadorPracticas"
ROL_ESTUDIANTE = "Estudiante"
ESTADOS_CON_PDF = (EstadoActa.GENERADA, EstadoActa.APROBADA)
TIPO_PDF = "application/pdf"


class ExportarActa:
    """Entrega el PDF guardado por el Worker de actas; nunca lo compone."""

    def __init__(
        self,
        repositorio: RepositorioPracticas,
        bitacora: Bitacora,
        almacen: AlmacenActas,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._repositorio = repositorio
        self._bitacora = bitacora
        self._almacen = almacen
        self._reloj = reloj

    def ejecutar(self, solicitud: SolicitudExportacionActa) -> ActaExportada:
        """Valida el acceso y el estado del acta y devuelve su PDF."""
        usuario = solicitud.usuario
        acta = self._repositorio.obtener_acta(solicitud.id_acta)
        if acta is None:
            raise ActaNoEncontrada(solicitud.id_acta)

        practica = self._repositorio.obtener_practica(acta.id_practica)
        autorizado = usuario.rol == ROL_COORDINADOR or (
            usuario.rol == ROL_ESTUDIANTE and practica.id_estudiante == usuario.id
        )
        if not autorizado:
            self._bitacora.registrar(
                usuario.id, usuario.rol, f"acta:{acta.id}", "exportar acta", self._reloj()
            )
            raise AccesoDenegado()

        if acta.estado not in ESTADOS_CON_PDF or acta.ruta_pdf is None:
            raise ActaNoExportable("el acta no tiene PDF generado")

        contenido = self._almacen.leer(acta.ruta_pdf)  # AlmacenNoDisponible si falla (ADR-007)
        return ActaExportada(acta.id, f"acta-{acta.id}.pdf", TIPO_PDF, contenido)
