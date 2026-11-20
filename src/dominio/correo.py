"""Correo: regla de formato de los correos de tutores, estudiantes y representantes (CU-13, CU-14)."""

import re

FORMATO_CORREO = re.compile(r"[^@\s]+@[^@\s]+\.[^@\s]+")


class Correo:
    """Valida el formato de un correo; no comprueba que el buzon exista."""

    @staticmethod
    def es_valido(texto: str) -> bool:
        """Un correo valido tiene usuario, una arroba y un dominio con punto, sin espacios."""
        return bool(texto) and FORMATO_CORREO.fullmatch(texto) is not None
