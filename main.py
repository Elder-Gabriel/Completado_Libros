import os
import logging
import argparse
import json
from modules.parser import parse_user_prompt
from modules.content_builder import generate_book_content
from modules.image_generator import generate_book_images
from modules.pdf_creator import assemble_pdf

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
    print("\n📘 === Generación de libro TEI ===")
    title = input("📚 Título del libro: ").strip()
    audience = input("👥 Público objetivo (niños, jóvenes, adultos): ").strip().lower()
    age_range = input("🎯 Rango de edad (ej. 7-12, 18-25): ").strip()
    
    # Eliminamos la solicitud de número de páginas
    
    return {
        "title": title,
        "audience": audience,
        "age_range": age_range,
        # Eliminamos "pages" del diccionario ya que no lo pedimos
    }

def limpiar_nombre_archivo(nombre):
    return nombre.lower().replace(" ", "_").replace(":", "").replace("¿", "").replace("?", "").replace("¡", "").replace("!", "")

def generar_libro(titulo, publico, edad, ruta_salida=None):
    """
    Función para generar un libro desde la interfaz gráfica
    
    Args:
        titulo (str): Título del libro
        publico (str): Público objetivo (Niños, Jóvenes, Adultos)
        edad (str): Rango de edad sugerida
        ruta_salida (str, optional): Ruta personalizada para guardar el PDF
        
    Returns:
        str: Ruta del archivo PDF generado
    """
    try:
        # 1. Crear parámetros del libro
        book_params = {
            "title": titulo,
            "audience": publico.lower(),
            "age_range": edad
        }

        # 2. Definir nombre de salida
        if ruta_salida:
            output_pdf = ruta_salida
        else:
            output_pdf = f"{limpiar_nombre_archivo(book_params['title'])}.pdf"
        
        output_dir = os.path.dirname(output_pdf) or "."
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

        # 5. Crear PDF
        logger.info("📦 Ensamblando PDF final...")
        pdf_path = assemble_pdf(book_content, images, output_pdf)
        logger.info(f"✅ ¡Libro generado exitosamente! PDF en: {pdf_path}")
        
        return pdf_path

    except Exception as e:
        logger.exception("❌ Error en la generación del libro:")
        raise

def main():
    parser = argparse.ArgumentParser(description="Generador de Libros Digitales TEI")
    parser.add_argument("--output", "-o", type=str, help="Ruta para guardar el PDF final")
    parser.add_argument("--no-temp", action="store_true", help="No guardar archivos temporales")
    args = parser.parse_args()

    try:
        # 1. Obtener parámetros del libro
        book_params = obtener_parametros()

        # 2. Definir nombre de salida
        if args.output:
            output_pdf = args.output
        else:
            output_pdf = f"{limpiar_nombre_archivo(book_params['title'])}.pdf"
        output_dir = os.path.dirname(output_pdf) or "."
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

        # 5. Crear PDF
        logger.info("📦 Ensamblando PDF final...")
        pdf_path = assemble_pdf(book_content, images, output_pdf)
        logger.info(f"✅ ¡Libro generado exitosamente! PDF en: {pdf_path}")

    except Exception as e:
        logger.exception("❌ Error en la generación del libro:")
        raise

if __name__ == "__main__":
    main()