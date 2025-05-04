import os
import logging
import argparse
import json
from modules.parser import parse_user_prompt
from modules.content_builder import generate_book_content
from modules.image_generator import generate_book_images
from modules.epub_creator import assemble_epub  # Cambiado de pdf_creator a epub_creator

# Configuración del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("tei.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def obtener_parametros():
    print("\n📘 === Generación de libro TEI en formato EPUB ===")
    title = input("📚 Título del libro: ").strip()
    tema = input("🔍 Tema principal del libro: ").strip()
    publico = input("👥 Público objetivo (niños, jóvenes, adultos): ").strip().lower()
    edad = input("🎯 Rango de edad (ej. 7-12, 18-25): ").strip()
    nivel_academico = input("🎓 Nivel académico (básico, intermedio, universitario): ").strip().lower()
    enfoque = input("🧩 Enfoque (teórico, práctico, paso a paso): ").strip().lower()
    formato_idioma = input("💬 Formato del lenguaje (formal, casual, técnico): ").strip().lower()
    paginas_deseadas = input("📏 Número aproximado de páginas: ").strip()
    profundidad = input("🔬 Nivel de profundidad (superficial, medio, profundo): ").strip().lower()
    
    return {
        "title": title,
        "tema": tema,
        "publico": publico,
        "edad": edad,
        "nivel_academico": nivel_academico,
        "enfoque": enfoque,
        "formato_idioma": formato_idioma,
        "paginas_deseadas": paginas_deseadas,
        "profundidad": profundidad
    }

def limpiar_nombre_archivo(nombre):
    return nombre.lower().replace(" ", "_").replace(":", "").replace("¿", "").replace("?", "").replace("¡", "").replace("!", "")

def generar_libro(titulo, tema, publico, edad, nivel_academico, enfoque, formato_idioma, paginas_deseadas, profundidad, ruta_salida=None):
    """
    Función para generar un libro desde la interfaz gráfica
    
    Args:
        titulo (str): Título del libro
        tema (str): Tema principal del libro
        publico (str): Público objetivo (Niños, Jóvenes, Adultos)
        edad (str): Rango de edad sugerida
        nivel_academico (str): Nivel académico
        enfoque (str): Enfoque del libro
        formato_idioma (str): Formato del lenguaje
        paginas_deseadas (str): Número aproximado de páginas
        profundidad (str): Nivel de profundidad
        ruta_salida (str, optional): Ruta personalizada para guardar el EPUB
        
    Returns:
        str: Ruta del archivo EPUB generado
    """
    try:
        # 1. Crear parámetros del libro
        book_params = {
            "title": titulo,
            "tema": tema,
            "publico": publico.lower(),
            "edad": edad,
            "nivel_academico": nivel_academico,
            "enfoque": enfoque,
            "formato_idioma": formato_idioma,
            "paginas_deseadas": paginas_deseadas,
            "profundidad": profundidad
        }

        # 2. Definir nombre de salida
        if ruta_salida:
            output_epub = ruta_salida
        else:
            output_epub = f"{limpiar_nombre_archivo(book_params['title'])}.epub"
        
        output_dir = os.path.dirname(output_epub) or "."
        os.makedirs(output_dir, exist_ok=True)

        # 3. Generar contenido del libro (estructura base)
        logger.info("🧠 Generando contenido del libro...")
        book_content = generate_book_content(book_params)

        # Guardar contenido temporal
        content_path = os.path.join(output_dir, "book_content.json")
        with open(content_path, "w", encoding="utf-8") as f:
            json.dump(book_content, f, indent=2, ensure_ascii=False)
        logger.info(f"📄 Contenido guardado en: {content_path}")

        # 4. Generar imágenes del libro
        logger.info("🖼️ Generando imágenes del libro...")
        images_dir = os.path.join(output_dir, "images")
        images = generate_book_images(book_content, book_params, images_dir)

        # Guardar información de imágenes
        images_path = os.path.join(output_dir, "images_info.json")
        with open(images_path, "w", encoding="utf-8") as f:
            json.dump(images, f, indent=2)
        logger.info(f"🗂️ Info de imágenes guardada en: {images_path}")

        # 5. Crear EPUB
        logger.info("📦 Ensamblando EPUB final...")
        epub_path = assemble_epub(book_content, images, output_epub)
        logger.info(f"✅ ¡Libro generado exitosamente! EPUB en: {epub_path}")
        
        return epub_path

    except Exception as e:
        logger.exception("❌ Error en la generación del libro:")
        raise

def main():
    parser = argparse.ArgumentParser(description="Generador de Libros Digitales TEI en formato EPUB")
    parser.add_argument("--output", "-o", type=str, help="Ruta para guardar el EPUB final")
    parser.add_argument("--no-temp", action="store_true", help="No guardar archivos temporales")
    args = parser.parse_args()

    try:
        # 1. Obtener parámetros del libro
        book_params = obtener_parametros()

        # 2. Definir nombre de salida
        if args.output:
            output_epub = args.output
        else:
            output_epub = f"{limpiar_nombre_archivo(book_params['title'])}.epub"
        output_dir = os.path.dirname(output_epub) or "."
        os.makedirs(output_dir, exist_ok=True)

        # 3. Generar contenido del libro (estructura base)
        logger.info("🧠 Generando contenido del libro...")
        book_content = generate_book_content(book_params)

        if not args.no_temp:
            content_path = os.path.join(output_dir, "book_content.json")
            with open(content_path, "w", encoding="utf-8") as f:
                json.dump(book_content, f, indent=2, ensure_ascii=False)
            logger.info(f"📄 Contenido guardado en: {content_path}")

        # 4. Generar imágenes del libro
        logger.info("🖼️ Generando imágenes del libro...")
        images_dir = os.path.join(output_dir, "images")
        images = generate_book_images(book_content, book_params, images_dir)

        if not args.no_temp:
            images_path = os.path.join(output_dir, "images_info.json")
            with open(images_path, "w", encoding="utf-8") as f:
                json.dump(images, f, indent=2)
            logger.info(f"🗂️ Info de imágenes guardada en: {images_path}")

        # 5. Crear EPUB
        logger.info("📦 Ensamblando EPUB final...")
        epub_path = assemble_epub(book_content, images, output_epub)
        logger.info(f"✅ ¡Libro generado exitosamente! EPUB en: {epub_path}")

    except Exception as e:
        logger.exception("❌ Error en la generación del libro:")
        raise

if __name__ == "__main__":
    main()