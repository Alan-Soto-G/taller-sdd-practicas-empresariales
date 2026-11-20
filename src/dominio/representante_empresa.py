"""RepresentanteEmpresa: supervisor de la Empresa que evalua al practicante, sin cuenta institucional (vista logica, ADR-005)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class RepresentanteEmpresa:
    id: str
    id_empresa: str
    nombre: str
    correo: str
