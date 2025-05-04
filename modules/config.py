"""
Configuraciones para el generador de libros educativos EPUB.
"""

import os
from pathlib import Path

# Directorios del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = os.path.join(BASE_DIR, "output")
TEMP_DIR = os.path.join(BASE_DIR, "temp")
IMAGES_DIR = os.path.join(TEMP_DIR, "images")

# Crear directorios si no existen
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(IMAGES_DIR, exist_ok=True)

# Configuración API
OPENAI_API_MODEL = "gpt-4o"  # Modelo para generación de contenido
OPENAI_IMAGE_MODEL = "dall-e-3"  # Modelo para generación de imágenes
IMAGE_SIZE = "1024x1024"  # Tamaño de las imágenes generadas
IMAGE_QUALITY = "standard"  # Calidad de las imágenes: "standard" o "hd"

# Límites y parámetros
MAX_CHAPTERS = 10  # Número máximo de capítulos
MAX_IMAGES = 15  # Número máximo de imágenes a generar
MIN_CONTENT_LENGTH = 500  # Longitud mínima de contenido por capítulo
MAX_CONTENT_LENGTH = 5000  # Longitud máxima de contenido por capítulo

# Configuración EPUB
EPUB_STYLESHEET = """
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