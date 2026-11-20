"""DTO de salida del caso de uso RegistrarEvaluacion (CU-06)."""

from dataclasses import dataclass

from dominio.estado_practica import EstadoPractica


@dataclass(frozen=True)
class EvaluacionRegistrada:
    id: str
    id_practica: str
    estado_practica: EstadoPractica
