"""ActaFinal: documento que cierra la Practica; la API la registra en generacion y el Worker de actas la genera (vista logica, ADR-001)."""

from dataclasses import dataclass, replace
from datetime import datetime

from dominio.estado_acta import EstadoActa


@dataclass(frozen=True)
class ActaFinal:
    id: str
    id_practica: str
    fecha_solicitud: datetime
    estado: EstadoActa
    ruta_pdf: str | None = None

    @classmethod
    def solicitar(cls, id: str, id_practica: str, ahora: datetime) -> "ActaFinal":
        """Crea el acta en generacion; la compone despues el Worker de actas (ADR-001)."""
        return cls(id, id_practica, ahora, EstadoActa.EN_GENERACION)

    def marcar_generada(self, ruta_pdf: str) -> "ActaFinal":
        """Regla de CU-07: el acta en generacion queda generada con la ruta de su PDF (ADR-003)."""
        if self.estado != EstadoActa.EN_GENERACION:
            raise ValueError("el acta no está en generación")
        return replace(self, estado=EstadoActa.GENERADA, ruta_pdf=ruta_pdf)

    def marcar_con_error(self) -> "ActaFinal":
        """Regla de CU-07: el acta que agota los intentos queda con error (ADR-001, DT-01)."""
        if self.estado != EstadoActa.EN_GENERACION:
            raise ValueError("el acta no está en generación")
        return replace(self, estado=EstadoActa.CON_ERROR)

    def aprobar(self) -> "ActaFinal":
        """Regla de CU-08: con las tres aprobaciones, el acta generada queda aprobada (ADR-006)."""
        if self.estado != EstadoActa.GENERADA:
            raise ValueError("el acta no está generada")
        return replace(self, estado=EstadoActa.APROBADA)
