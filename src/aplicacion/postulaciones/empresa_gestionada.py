"""DTO de salida de GestionarEmpresas: la Empresa con su representante, si lo tiene (CU-14)."""

from dataclasses import dataclass


@dataclass(frozen=True)
class EmpresaGestionada:
    id: str
    razon_social: str
    nit: str
    id_representante: str | None
    nombre_representante: str | None
    correo_representante: str | None
