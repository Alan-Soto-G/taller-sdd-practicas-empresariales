"""DTO de salida del caso de uso PublicarPlaza (CU-02)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PlazaPublicada:
    id: str
    id_empresa: str
    cargo: str
    cupos: int
    periodo: str
