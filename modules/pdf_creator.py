import os
import logging
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from config import (
    PDF_MARGIN, FONT_SIZE_TITLE, FONT_SIZE_HEADING,
    FONT_SIZE_SUBHEADING, FONT_SIZE_BODY
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFCreator:
    def __init__(self, output_path):
        self.output_path = output_path
        self.c = canvas.Canvas(output_path, pagesize=A4)
        self.width, self.height = A4
        self.page_number = 1
        self.y_position = self.height - PDF_MARGIN
        self.styles = getSampleStyleSheet()

        # Define custom styles
        self.custom_title = ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Title'],
            fontSize=FONT_SIZE_TITLE,
            alignment=TA_CENTER,
            spaceAfter=30
        )
        self.custom_heading1 = ParagraphStyle(
            name='CustomHeading1',
            parent=self.styles['Heading1'],
            fontSize=FONT_SIZE_HEADING,
            spaceAfter=20
        )
        self.custom_heading2 = ParagraphStyle(
            name='CustomHeading2',
            parent=self.styles['Heading2'],
            fontSize=FONT_SIZE_SUBHEADING,
            spaceAfter=15
        )
        self.custom_body = ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=FONT_SIZE_BODY,
            alignment=TA_JUSTIFY,
            spaceAfter=12
        )

    def add_title_page(self, title, subtitle=None, cover_image_path=None):
        # Draw title
        p = Paragraph(title, self.custom_title)
        w, h = p.wrap(self.width - 2*PDF_MARGIN, self.height)
        p.drawOn(self.c, PDF_MARGIN, self.height - PDF_MARGIN - h)

        # Draw subtitle
        if subtitle:
            sub = Paragraph(subtitle, self.custom_heading2)
            w2, h2 = sub.wrap(self.width - 2*PDF_MARGIN, self.height)
            sub.drawOn(self.c, PDF_MARGIN, self.height - PDF_MARGIN - h - h2)

        # Draw cover image
        if cover_image_path and os.path.exists(cover_image_path):
            img_width = self.width / 2
            img_height = img_width * 0.75
            x = (self.width - img_width) / 2
            y = self.height/2 - img_height/2
            self.c.drawImage(cover_image_path, x, y, img_width, img_height)

        self.c.showPage()
        self.y_position = self.height - PDF_MARGIN
        self.page_number += 1

    def add_paragraph(self, text, style):
        # Create and draw paragraph, handle page breaks
        paragraph = Paragraph(text, style)
        w, h = paragraph.wrap(self.width - 2*PDF_MARGIN, self.y_position)
        if self.y_position - h < PDF_MARGIN:
            self.c.showPage()
            self.y_position = self.height - PDF_MARGIN
            self.page_number += 1
            paragraph = Paragraph(text, style)
            w, h = paragraph.wrap(self.width - 2*PDF_MARGIN, self.y_position)
        paragraph.drawOn(self.c, PDF_MARGIN, self.y_position - h)
        self.y_position -= (h + 10)

    def add_heading1(self, text):
        self.add_paragraph(text, self.custom_heading1)

    def add_heading2(self, text):
        self.add_paragraph(text, self.custom_heading2)

    def add_image(self, image_path, width=200, height=200):
        # Center the image
        if not os.path.exists(image_path):
            return
        if self.y_position - height < PDF_MARGIN:
            self.c.showPage()
            self.y_position = self.height - PDF_MARGIN
            self.page_number += 1
        x = (self.width - width) / 2
        y = self.y_position - height
        self.c.drawImage(image_path, x, y, width, height)
        self.y_position = y - 20

    def assemble_pdf(self, book_content, images, output_pdf):
        logger.info("Iniciando ensamblado del PDF...")

        # Title page with optional cover image
        cover = next((i for i in images if i.get('type') == 'cover'), None)
        self.add_title_page(
            book_content.get('title', 'Sin título'),
            subtitle='Generado por TEI',
            cover_image_path=cover['path'] if cover else None
        )

        # Introduction - AQUÍ ESTÁ LA CORRECCIÓN
        intro = book_content.get('introduction', '')
        if intro:
            self.add_heading1('Introducción')
            if isinstance(intro, dict):
                self.add_paragraph(intro.get('content', ''), self.custom_body)
            else:
                self.add_paragraph(intro, self.custom_body)

        # Chapters
        chapter_imgs = [i['path'] for i in images if i.get('type') == 'chapter']
        for idx, chap in enumerate(book_content.get('chapters', [])):
            self.add_heading1(chap.get('title', ''))
            # Chapter summary/content
            content = chap.get('content', '')
            if content:
                self.add_paragraph(content, self.custom_body)
            # Sections
            for sec in chap.get('sections', []):
                self.add_heading2(sec.get('title', ''))
                self.add_paragraph(sec.get('content', ''), self.custom_body)
            # Chapter image
            if idx < len(chapter_imgs):
                self.add_image(chapter_imgs[idx])

        # Exercises
        exercises_img = next((i for i in images if i.get('type') == 'exercises'), None)
        exercises = book_content.get('exercises', [])
        if exercises:
            self.add_heading1('Ejercicios de Repaso')
            # If exercises is a list of strings
            if isinstance(exercises, list):
                for ex in exercises:
                    self.add_paragraph(ex, self.custom_body)
            # Single string
            else:
                self.add_paragraph(exercises, self.custom_body)
            if exercises_img:
                self.add_image(exercises_img['path'])

        # Conclusion
        concl_img = next((i for i in images if i.get('type') == 'conclusion'), None)
        concl = book_content.get('conclusion', '')
        if concl:
            self.add_heading1('Conclusión')
            self.add_paragraph(concl, self.custom_body)
            if concl_img:
                self.add_image(concl_img['path'])

        # Bibliography
        biblio = book_content.get('bibliography', [])
        if biblio:
            self.add_heading1('Bibliografía')
            if isinstance(biblio, list):
                biblio_text = "\n".join([f"• {ref}" for ref in biblio])
                self.add_paragraph(biblio_text, self.custom_body)
            else:
                self.add_paragraph(biblio, self.custom_body)

        # Save
        self.c.save()
        logger.info(f"PDF guardado exitosamente en: {output_pdf}")
        return output_pdf


# Función directa para ensamblar el PDF
def assemble_pdf(book_content, images, output_pdf):
    """
    Crea y ensambla un PDF con el contenido del libro y las imágenes proporcionadas.
    
    Args:
        book_content (dict): Contenido estructurado del libro
        images (list): Lista de diccionarios con información de imágenes
        output_pdf (str): Ruta donde se guardará el PDF generado
        
    Returns:
        str: Ruta al archivo PDF generado
    """
    pdf = PDFCreator(output_pdf)
    return pdf.assemble_pdf(book_content, images, output_pdf)