import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import lightgrey, red


class ReportGenerator:
    def __init__(self, base_dir="media/reports"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def generate_report(self, user_data: dict, analysis_data: dict) -> str:
        """
        Gera um PDF de laudo automatizado.
        Retorna o caminho do arquivo.
        """

        filename = f"laudo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = os.path.join(self.base_dir, filename)

        c = canvas.Canvas(file_path, pagesize=A4)
        width, height = A4

        self._watermark(c, width, height)
        self._header(c, height)
        self._user_section(c, user_data, height)
        self._analysis_section(c, analysis_data, height)
        self._ethical_warning(c)
        self._footer(c, width)

        c.showPage()
        c.save()

        return file_path

    # =======================
    # SEÇÕES DO PDF
    # =======================

    def _header(self, c, height):
        c.setFont("Helvetica-Bold", 16)
        c.drawString(2 * cm, height - 2 * cm, "Laudo de Análise Automatizada")

        c.setFont("Helvetica", 9)
        c.drawString(
            2 * cm,
            height - 2.7 * cm,
            f"Emitido em: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        )

    def _user_section(self, c, user_data, height):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, height - 4 * cm, "Dados do Utilizador")

        c.setFont("Helvetica", 10)
        y = height - 5 * cm

        for key, value in user_data.items():
            c.drawString(2 * cm, y, f"{key}: {value}")
            y -= 0.6 * cm

    def _analysis_section(self, c, analysis_data, height):
        c.setFont("Helvetica-Bold", 12)
        c.drawString(2 * cm, height - 9 * cm, "Resultado da Análise")

        c.setFont("Helvetica", 10)
        y = height - 10 * cm

        for key, value in analysis_data.items():
            c.drawString(2 * cm, y, f"{key}: {value}")
            y -= 0.6 * cm

    def _ethical_warning(self, c):
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(red)
        c.drawString(2 * cm, 3.2 * cm, "Aviso Ético e Legal")

        c.setFont("Helvetica", 8)
        text = (
            "Este documento foi gerado automaticamente por um sistema de "
            "inteligência artificial. Ele não substitui avaliação profissional "
            "humana, diagnóstico clínico ou parecer técnico oficial. "
            "O uso das informações é de inteira responsabilidade do utilizador."
        )

        text_obj = c.beginText(2 * cm, 2.6 * cm)
        for line in text.split(". "):
            text_obj.textLine(line.strip())
        c.drawText(text_obj)

        c.setFillColor(lightgrey)

    def _watermark(self, c, width, height):
        c.saveState()
        c.setFont("Helvetica-Bold", 48)
        c.setFillColor(lightgrey)
        c.translate(width / 2, height / 2)
        c.rotate(45)
        c.drawCentredString(0, 0, "CONFIDENCIAL")
        c.restoreState()

    def _footer(self, c, width):
        c.setFont("Helvetica", 8)
        c.setFillColor(lightgrey)
        c.drawCentredString(
            width / 2,
            1.5 * cm,
            "Sistema Automatizado • Documento protegido • Uso restrito"
        )
