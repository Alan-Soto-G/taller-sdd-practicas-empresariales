"""Empresa: empresa aliada con convenio vigente que ofrece plazas; NIT y razon social (vista logica, CU-02, CU-14)."""

import re
from dataclasses import dataclass

FORMATO_NIT = re.compile(r"\d{9}-\d")


@dataclass(frozen=True)
class Empresa:
    id: str
    razon_social: str
    nit: str = ""

    @staticmethod
    def motivo_invalidez(razon_social: str, nit: str) -> str | None:
        """Regla de CU-14: razon social obligatoria y NIT con 9 digitos, guion y digito de verificacion."""
        if not razon_social or not razon_social.strip():
            return "la razón social es obligatoria"
        if not FORMATO_NIT.fullmatch(nit or ""):
            return "el NIT debe tener 9 dígitos, un guion y el dígito de verificación"
        return None
