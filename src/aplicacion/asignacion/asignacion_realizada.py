"""DTO de salida del caso de uso AsignarTutor: un resultado por Practica, en el orden recibido (CU-03)."""

from dataclasses import dataclass

from aplicacion.asignacion.resultado_practica import ResultadoPractica


@dataclass(frozen=True)
class AsignacionRealizada:
    id_tutor: str
    resultados: tuple[ResultadoPractica, ...]
