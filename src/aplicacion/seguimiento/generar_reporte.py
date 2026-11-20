"""Caso de uso CU-11: el Coordinador genera el reporte de practicas, actas y horas (Modulo Seguimiento; ADR-004, ADR-006, ADR-007)."""

from collections import Counter
from collections.abc import Callable
from datetime import datetime

from aplicacion.actas.consultar_acta_practica import ConsultarActaPractica
from aplicacion.errores.acceso_denegado import AccesoDenegado
from aplicacion.errores.empresa_no_encontrada import EmpresaNoEncontrada
from aplicacion.horas.resumir_horas_practica import ResumirHorasPractica
from aplicacion.puertos.bitacora import Bitacora
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas
from aplicacion.seguimiento.reporte_practicas import ReportePracticas
from aplicacion.seguimiento.solicitud_reporte import SolicitudReporte
from dominio.estado_acta import EstadoActa
from dominio.estado_practica import EstadoPractica

ROL_COORDINADOR = "CoordinadorPracticas"
SIN_TUTOR = "sin tutor"
SIN_ACTA = "sin acta"


class GenerarReporte:
    """Calcula el reporte sobre los datos actuales; solo lee, no guarda nada."""

    def __init__(
        self,
        repositorio: RepositorioPracticas,
        bitacora: Bitacora,
        resumir_horas: ResumirHorasPractica,
        consultar_acta: ConsultarActaPractica,
        reloj: Callable[[], datetime] = datetime.now,
    ) -> None:
        self._repositorio = repositorio
        self._bitacora = bitacora
        self._resumir_horas = resumir_horas
        self._consultar_acta = consultar_acta
        self._reloj = reloj

    def ejecutar(self, solicitud: SolicitudReporte) -> ReportePracticas:
        """Devuelve los conteos del reporte general o de una Empresa."""
        usuario = solicitud.usuario
        ahora = self._reloj()
        if usuario.rol != ROL_COORDINADOR:
            self._bitacora.registrar(usuario.id, usuario.rol, "reportes", "generar reporte", ahora)
            raise AccesoDenegado()

        practicas = self._repositorio.listar_practicas()
        if solicitud.id_empresa is not None:
            if self._repositorio.obtener_empresa(solicitud.id_empresa) is None:
                raise EmpresaNoEncontrada(solicitud.id_empresa)
            practicas = [p for p in practicas if p.id_empresa == solicitud.id_empresa]

        por_estado = {str(estado): 0 for estado in EstadoPractica}
        actas_por_estado = {SIN_ACTA: 0} | {str(estado): 0 for estado in EstadoActa}
        por_empresa: Counter[str] = Counter()
        por_tutor: Counter[str] = Counter()
        horas_aprobadas = 0
        for practica in practicas:
            por_estado[str(practica.estado)] += 1
            por_empresa[practica.id_empresa] += 1
            por_tutor[practica.id_tutor or SIN_TUTOR] += 1
            acta = self._consultar_acta.ejecutar(practica.id)
            actas_por_estado[SIN_ACTA if acta is None else str(acta.estado)] += 1
            horas_aprobadas += self._resumir_horas.ejecutar(
                practica.id, practica.version_regla
            ).horas_aprobadas

        return ReportePracticas(
            solicitud.id_empresa,
            len(practicas),
            por_estado,
            dict(sorted(por_empresa.items())),
            dict(sorted(por_tutor.items())),
            actas_por_estado,
            horas_aprobadas,
            ahora,
        )
