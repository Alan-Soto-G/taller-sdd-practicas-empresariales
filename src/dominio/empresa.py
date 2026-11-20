"""Empresa: empresa aliada con convenio vigente que ofrece plazas (vista logica, CU-02)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Empresa:
    id: str
    razon_social: str
