"""RepresentanteEmpresa: supervisor de la Empresa que evalua al practicante, sin cuenta institucional (vista logica, ADR-005)."""

from dataclasses import dataclass

from dominio.correo import Correo


@dataclass(frozen=True)
class RepresentanteEmpresa:
    id: str
    id_empresa: str
    nombre: str
    correo: str

    @staticmethod
    def motivo_invalidez(nombre: str, correo: str) -> str | None:
        """Regla de CU-14: nombre obligatorio y correo valido, porque a ese correo llegan los enlaces (ADR-005)."""
        if not nombre or not nombre.strip():
            return "el nombre del representante es obligatorio"
        if not Correo.es_valido(correo):
            return "el correo no es válido"
        return None
