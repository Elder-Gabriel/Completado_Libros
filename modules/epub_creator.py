import os
import logging
import ebooklib
from ebooklib import epub
from bs4 import BeautifulSoup
from datetime import datetime

logger = logging.getLogger(__name__)

# Estilo CSS básico para el libro
DEFAULT_CSS = """
body {
    font-family: "Helvetica", "Arial", sans-serif;
    margin: 5%;
    text-align: justify;
    line-height: 1.5;
}
h1 {
    text-align: center;
    font-size: 2em;
    margin-bottom: 1em;
    page-break-before: always;
}
h2 {
    font-size: 1.5em;
    margin-top: 1em;
    margin-bottom: 0.7em;
}
h3 {
    font-size: 1.3em;
    margin-top: 0.8em;
    margin-bottom: 0.5em;
}
p {
    margin-bottom: 0.5em;
}
img {
    max-width: 100%;
    display: block;
    margin: 1em auto;
}
.cover {
    text-align: center;
    padding: 0;
    margin: 0;
}
.cover img {
    max-height: 100%;
    max-width: 100%;
}
.toc-title {
    text-align: center;
    font-size: 2em;
    margin-bottom: 1em;
}
.toc-entry {
    margin-bottom: 0.5em;
}
.exercise {
    background-color: #f7f7f7;
    padding: 1em;
    margin: 1em 0;
    border-left: 5px solid #4a7ba7;
}
.exercise h3 {
    color: #4a7ba7;
    margin-top: 0;
}
.bibliography {
    margin-top: 2em;
}
.bibliography-item {
    margin-bottom: 0.5em;
    text-indent: -2em;
    padding-left: 2em;
}
"""

def clean_html(html_content):
    """Limpia y formatea HTML para usar en EPUB."""
    soup = BeautifulSoup(html_content, 'lxml')
    return str(soup)

def create_cover_html(book_content):
    """Crea la página de portada HTML."""
    html = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>{book_content["title"]}</title>
        <link rel="stylesheet" type="text/css" href="style.css" />
    </head>
    <body>
        <div class="cover">
            <h1>{book_content["title"]}</h1>
            <p>{book_content["description"]}</p>
        </div>
    </body>
    </html>"""
    return clean_html(html)

def create_toc_html(book_content):
    """Crea la página del índice HTML."""
    toc_items = ""
    for chapter_number, (chapter_title, page) in enumerate(book_content["toc"].items(), 1):
        toc_items += f'<div class="toc-entry">{chapter_number}. {chapter_title} - {page}</div>\n'
    
    html = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>Índice - {book_content["title"]}</title>
        <link rel="stylesheet" type="text/css" href="style.css" />
    </head>
    <body>
        <h1 class="toc-title">Índice</h1>
        {toc_items}
    </body>
    </html>"""
    return clean_html(html)

def create_introduction_html(book_content):
    """Crea la página de introducción HTML."""
    html = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>Introducción - {book_content["title"]}</title>
        <link rel="stylesheet" type="text/css" href="style.css" />
    </head>
    <body>
        <h1>Introducción</h1>
        <div>{book_content["introduction"]}</div>
    </body>
    </html>"""
    return clean_html(html)

def create_chapter_html(chapter, chapter_number, book_title, images=None):
    """Crea la página HTML para un capítulo."""
    content = chapter["content"]
    
    # Si hay imágenes disponibles, insertar en el contenido
    if images and f"chapter_{chapter_number}" in images:
        chapter_images = images[f"chapter_{chapter_number}"]
        for img_idx, img_info in enumerate(chapter_images):
            img_tag = f'<img src="{os.path.basename(img_info["path"])}" alt="{img_info["description"]}" />'
            # Insertar la imagen después de un párrafo apropiado
            paragraphs = content.split('\n\n')
            if len(paragraphs) > (img_idx + 1) * 2:  # Asegurar que hay suficientes párrafos
                insert_point = (img_idx + 1) * 2  # Insertar después de cada segundo párrafo
                paragraphs.insert(insert_point, img_tag)
            else:
                paragraphs.append(img_tag)  # Añadir al final si no hay suficientes párrafos
            content = '\n\n'.join(paragraphs)
    
    html = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>Capítulo {chapter_number} - {book_title}</title>
        <link rel="stylesheet" type="text/css" href="style.css" />
    </head>
    <body>
        <h1>{chapter["title"]}</h1>
        <div>{content}</div>
    </body>
    </html>"""
    return clean_html(html)

def create_exercises_html(book_content):
    """Crea la página HTML para ejercicios."""
    exercises_html = ""
    for idx, exercise in enumerate(book_content["exercises"], 1):
        exercises_html += f"""
        <div class="exercise">
            <h3>Ejercicio {idx}: {exercise["title"]}</h3>
            <p>{exercise["description"]}</p>
        </div>
        """
    
    html = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>Ejercicios - {book_content["title"]}</title>
        <link rel="stylesheet" type="text/css" href="style.css" />
    </head>
    <body>
        <h1>Ejercicios y Actividades</h1>
        {exercises_html}
    </body>
    </html>"""
    return clean_html(html)

def create_conclusion_html(book_content):
    """Crea la página HTML para la conclusión."""
    html = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>Conclusión - {book_content["title"]}</title>
        <link rel="stylesheet" type="text/css" href="style.css" />
    </head>
    <body>
        <h1>Conclusión</h1>
        <div>{book_content["conclusion"]}</div>
    </body>
    </html>"""
    return clean_html(html)

def create_bibliography_html(book_content):
    """Crea la página HTML para la bibliografía."""
    references = ""
    for idx, reference in enumerate(book_content["bibliography"], 1):
        references += f'<p class="bibliography-item">{idx}. {reference}</p>\n'
    
    html = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>Bibliografía - {book_content["title"]}</title>
        <link rel="stylesheet" type="text/css" href="style.css" />
    </head>
    <body>
        <h1>Bibliografía</h1>
        <div class="bibliography">
            {references}
        </div>
    </body>
    </html>"""
    return clean_html(html)

def assemble_epub(book_content, images, output_path):
    """
    Crea un archivo EPUB a partir del contenido del libro e imágenes.
    
    Args:
        book_content (dict): Contenido del libro en formato JSON
        images (dict): Información sobre las imágenes generadas
        output_path (str): Ruta donde guardar el archivo EPUB
        
    Returns:
        str: Ruta del archivo EPUB generado
    """
    try:
        logger.info("📚 Creando estructura del EPUB...")
        
        # Crear un nuevo libro EPUB
        book = epub.EpubBook()
        
        # Establecer metadatos
        book.set_identifier(f"id-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        book.set_title(book_content["title"])
        book.set_language('es')
        
        # Añadir información adicional de metadatos
        if "publico" in book_content:
            book.add_metadata('DC', 'audience', book_content["publico"])
        if "tema" in book_content:
            book.add_metadata('DC', 'subject', book_content["tema"])
        
        # Añadir el archivo CSS
        style = epub.EpubItem(
            uid="style_default",
            file_name="style.css",
            media_type="text/css",
            content=DEFAULT_CSS
        )
        book.add_item(style)
        
        # Añadir imágenes al libro
        all_image_files = []
        for chapter_images in images.values():
            for img_info in chapter_images:
                img_path = img_info["path"]
                if os.path.exists(img_path):
                    img_name = os.path.basename(img_path)
                    with open(img_path, 'rb') as img_file:
                        img_content = img_file.read()
                    
                    # Determinar el tipo de contenido basado en la extensión
                    if img_path.lower().endswith('.jpg') or img_path.lower().endswith('.jpeg'):
                        media_type = 'image/jpeg'
                    elif img_path.lower().endswith('.png'):
                        media_type = 'image/png'
                    elif img_path.lower().endswith('.svg'):
                        media_type = 'image/svg+xml'
                    else:
                        media_type = 'image/jpeg'  # Por defecto
                    
                    # Añadir la imagen al EPUB
                    epub_image = epub.EpubItem(
                        file_name=img_name,
                        media_type=media_type,
                        content=img_content
                    )
                    book.add_item(epub_image)
                    all_image_files.append(img_name)
        
        # Crear capítulos
        chapters = []
        
        # Portada
        cover = epub.EpubHtml(title='Portada', file_name='cover.xhtml', lang='es')
        cover.content = create_cover_html(book_content)
        book.add_item(cover)
        chapters.append(cover)
        
        # Índice
        toc_page = epub.EpubHtml(title='Índice', file_name='toc.xhtml', lang='es')
        toc_page.content = create_toc_html(book_content)
        book.add_item(toc_page)
        chapters.append(toc_page)
        
        # Introducción
        intro = epub.EpubHtml(title='Introducción', file_name='introduction.xhtml', lang='es')
        intro.content = create_introduction_html(book_content)
        book.add_item(intro)
        chapters.append(intro)
        
        # Capítulos del libro
        for idx, chapter in enumerate(book_content["chapters"], 1):
            chapter_content = create_chapter_html(chapter, idx, book_content["title"], images)
            chapter_file = epub.EpubHtml(
                title=chapter["title"],
                file_name=f'chapter_{idx}.xhtml',
                lang='es'
            )
            chapter_file.content = chapter_content
            book.add_item(chapter_file)
            chapters.append(chapter_file)
        
        # Ejercicios
        exercises = epub.EpubHtml(title='Ejercicios', file_name='exercises.xhtml', lang='es')
        exercises.content = create_exercises_html(book_content)
        book.add_item(exercises)
        chapters.append(exercises)
        
        # Conclusión
        conclusion = epub.EpubHtml(title='Conclusión', file_name='conclusion.xhtml', lang='es')
        conclusion.content = create_conclusion_html(book_content)
        book.add_item(conclusion)
        chapters.append(conclusion)
        
        # Bibliografía
        bibliography = epub.EpubHtml(title='Bibliografía', file_name='bibliography.xhtml', lang='es')
        bibliography.content = create_bibliography_html(book_content)
        book.add_item(bibliography)
        chapters.append(bibliography)
        
        # Definir el orden de lectura
        book.spine = ['nav'] + chapters
        
        # Añadir tabla de contenidos en formato NCX y HTML
        book.toc = (
            (epub.Section('Libro'),
             (cover, toc_page, intro, *[chapters[i] for i in range(3, 3 + len(book_content["chapters"]))], 
              exercises, conclusion, bibliography)
            ),
        )
        
        # Añadir navegación de tabla de contenidos
        book.add_item(epub.EpubNcx())
        book.add_item(epub.EpubNav())
        
        # Escribir el archivo EPUB
        epub.write_epub(output_path, book, {})
        
        logger.info(f"📙 Archivo EPUB creado: {output_path}")
        return output_path
        
    except Exception as e:
        logger.exception(f"❌ Error al crear el EPUB: {str(e)}")
        raise