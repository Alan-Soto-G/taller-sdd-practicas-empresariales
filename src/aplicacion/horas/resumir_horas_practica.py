"""Caso de uso del Modulo Horas (solo lectura): resume las horas de una Practica para el Modulo Seguimiento (CU-09, ADR-002, ADR-008)."""

from aplicacion.configuracion.consultar_horas_requeridas import ConsultarHorasRequeridas
from aplicacion.horas.resumen_horas import ResumenHoras
from aplicacion.puertos.repositorio_practicas import RepositorioPracticas
from dominio.estado_registro_horas import EstadoRegistroHoras


class ResumirHorasPractica:
    """Suma las horas aprobadas y pendientes y las compara con las requeridas de la version de la Practica."""

    def __init__(
        self,
        repositorio: RepositorioPracticas,
        consultar_horas: ConsultarHorasRequeridas,
    ) -> None:
        self._repositorio = repositorio
        self._consultar_horas = consultar_horas

    def ejecutar(self, id_practica: str, version_regla: str) -> ResumenHoras:
        """Devuelve el resumen; el porcentaje es aprobadas sobre requeridas, entero y como maximo 100."""
        registros = self._repositorio.listar_registros_horas_de_practica(id_practica)
        aprobadas = sum(r.horas for r in registros if r.estado == EstadoRegistroHoras.APROBADO)
        pendientes = sum(r.horas for r in registros if r.estado == EstadoRegistroHoras.REPORTADO)
        requeridas = self._consultar_horas.ejecutar(version_regla)
        porcentaje = min(100, aprobadas * 100 // requeridas) if requeridas > 0 else 0
        return ResumenHoras(aprobadas, requeridas, pendientes, porcentaje)
