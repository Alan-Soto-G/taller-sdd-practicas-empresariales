"""Adaptador PDF: implementa ComponedorActa con ReportLab (BSD, codigo abierto; ADR-011) y traduce sus fallas a ActaNoComponible (ADR-007)."""

from io import BytesIO

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen.canvas import Canvas

from aplicacion.actas.datos_acta import DatosActa
from aplicacion.errores.acta_no_componible import ActaNoComponible

MARGEN = 72
INTERLINEA = 18
APROBADORES = ("Tutor", "Representante de la Empresa", "Coordinador de Prácticas")


class ComponedorActaReportlab:
    """Compone el acta final en un PDF de una pagina tamano carta."""

    def componer(self, datos: DatosActa) -> bytes:
        """Devuelve los bytes del PDF; cualquier falla de la libreria se traduce a ActaNoComponible."""
        try:
            return self._dibujar(datos)
        except Exception as error:
            raise ActaNoComponible() from error

    def _dibujar(self, datos: DatosActa) -> bytes:
        """Escribe el acta con la API de lienzo de ReportLab, sin comprimir las paginas."""
        salida = BytesIO()
        lienzo = Canvas(salida, pagesize=letter, pageCompression=0)
        lienzo.setTitle(f"Acta final {datos.id_acta}")
        _, alto = letter
        y = alto - MARGEN

        lienzo.setFont("Helvetica-Bold", 16)
        lienzo.drawString(MARGEN, y, f"ACTA FINAL DE PRÁCTICA EMPRESARIAL {datos.id_acta}")
        y -= 2 * INTERLINEA

        lienzo.setFont("Helvetica", 11)
        lineas = [
            f"Práctica: {datos.id_practica}",
            f"Estudiante: {datos.id_estudiante}",
            f"Empresa: {datos.id_empresa}",
            f"Tutor: {datos.id_tutor or 'sin tutor'}",
            f"Horas aprobadas: {datos.horas_aprobadas} de {datos.horas_requeridas} requeridas",
            f"Plantilla del acta: {datos.plantilla}",
            f"Solicitada: {datos.fecha_solicitud:%Y-%m-%d %H:%M}",
        ]
        for linea in lineas:
            lienzo.drawString(MARGEN, y, linea)
            y -= INTERLINEA

        y -= INTERLINEA
        lienzo.setFont("Helvetica-Bold", 12)
        lienzo.drawString(MARGEN, y, "Evaluación de desempeño de la empresa")
        y -= INTERLINEA
        lienzo.setFont("Helvetica", 11)
        for criterio, calificacion in datos.calificaciones.items():
            lienzo.drawString(MARGEN + 18, y, f"{criterio}: {calificacion}")
            y -= INTERLINEA
        if datos.observaciones:
            lienzo.drawString(MARGEN + 18, y, f"Observaciones: {datos.observaciones}")
            y -= INTERLINEA

        y -= INTERLINEA
        lienzo.setFont("Helvetica-Bold", 12)
        lienzo.drawString(MARGEN, y, "Aprobaciones electrónicas (CU-08)")
        y -= INTERLINEA
        lienzo.setFont("Helvetica", 11)
        for aprobador in APROBADORES:
            lienzo.drawString(MARGEN + 18, y, f"{aprobador}: pendiente")
            y -= INTERLINEA

        lienzo.showPage()
        lienzo.save()
        return salida.getvalue()
