"""Adaptador de Excel: implementa LectorExcel con openpyxl (MIT, codigo abierto; ADR-012) y traduce cualquier falla a ArchivoNoValido (ADR-007)."""

from io import BytesIO

from openpyxl import load_workbook

from aplicacion.errores.archivo_no_valido import ArchivoNoValido

MOTIVO = "el archivo no es un Excel .xlsx válido"


class LectorExcelOpenpyxl:
    """Lee cada hoja del libro: la fila 1 es el encabezado y las demas son datos, todo como texto."""

    def leer(self, contenido: bytes) -> dict[str, list[dict[str, str]]]:
        """Devuelve las filas de cada hoja; si el archivo no se puede leer, lanza ArchivoNoValido."""
        try:
            libro = load_workbook(BytesIO(contenido), read_only=True, data_only=True)
            try:
                return {hoja.title: self._filas(hoja) for hoja in libro.worksheets}
            finally:
                libro.close()
        except Exception as error:
            raise ArchivoNoValido(MOTIVO) from error

    def _filas(self, hoja) -> list[dict[str, str]]:
        """Convierte la hoja en filas por encabezado y quita las filas vacias del final."""
        filas = [tuple(self._texto(valor) for valor in fila) for fila in hoja.iter_rows(values_only=True)]
        while filas and not any(filas[-1]):
            filas.pop()
        if not filas:
            return []
        encabezado = filas[0]
        return [
            {encabezado[i]: valor for i, valor in enumerate(fila) if i < len(encabezado) and encabezado[i]}
            for fila in filas[1:]
        ]

    @staticmethod
    def _texto(valor: object) -> str:
        """Celda como texto: vacia → "", un decimal entero (3.0) → "3"."""
        if valor is None:
            return ""
        if isinstance(valor, float) and valor.is_integer():
            return str(int(valor))
        return str(valor).strip()
