import os
import logging
import openai
import requests
from io import BytesIO
from PIL import Image
from config import OPENAI_API_KEY, IMAGE_SIZE

# Configurar OpenAI
openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def generate_image(prompt: str, output_path: str = None) -> str:
    """
    Genera una imagen utilizando DALL-E basada en el prompt.
    
    Args:
        prompt (str): Descripción de la imagen a generar
        output_path (str, optional): Ruta para guardar la imagen. Si es None, se retorna la URL.
    
    Returns:
        str: Ruta local de la imagen guardada o URL de la imagen
    """
    try:
        logger.info(f"Generando imagen para prompt: {prompt[:50]}...")

        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size=IMAGE_SIZE
        )

        image_url = response.data[0].url
        logger.info(f"Imagen generada exitosamente: {image_url[:50]}...")

        # Si se proporciona una ruta de salida, descargar y guardar la imagen
        if output_path:
            img_response = requests.get(image_url)
            img = Image.open(BytesIO(img_response.content))

            # Crear directorio si no existe
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            img.save(output_path)
            logger.info(f"Imagen guardada en: {output_path}")
            return output_path

        return image_url

    except Exception as e:
        logger.error(f"Error al generar imagen: {str(e)}")
        # En caso de error, crear una imagen de placeholder
        try:
            if output_path:
                # Crear una imagen simple de placeholder
                placeholder = Image.new('RGB', (1024, 1024), color=(240, 240, 240))
                placeholder.save(output_path)
                logger.info(f"Imagen placeholder guardada en: {output_path}")
                return output_path
            else:
                return "https://via.placeholder.com/1024x1024.png?text=Error+al+generar+imagen"
        except Exception as placeholder_error:
            logger.error(f"Error al crear imagen placeholder: {str(placeholder_error)}")
            return ""

def generate_image_prompt(book_params: dict, description: str) -> str:
    """
    Genera un prompt para la creación de imágenes basado en los parámetros del libro y una descripción.
    
    Args:
        book_params (dict): Parámetros del libro, como el título y el público objetivo.
        description (str): Descripción adicional sobre la imagen.
    
    Returns:
        str: El prompt generado para la imagen.
    """
    # Combinamos los parámetros del libro con la descripción adicional para generar el prompt
    prompt = f"{description}. Público objetivo: {book_params['audience']}, Edad recomendada: {book_params['age_range']}, Título del libro: {book_params['title']}"
    return prompt

def generate_book_images(book_content: dict, book_params: dict, output_dir: str = "images") -> list:
    """
    Genera imágenes para el libro basado en su contenido.
    
    Args:
        book_content (dict): Contenido estructurado del libro
        book_params (dict): Parámetros del libro
        output_dir (str): Directorio para guardar las imágenes
    
    Returns:
        list: Lista de rutas de imágenes generadas
    """
    # Crear directorio de imágenes si no existe
    os.makedirs(output_dir, exist_ok=True)

    image_paths = []

    # Imagen para portada
    cover_prompt = generate_image_prompt(
        book_params,
        f"Portada ilustrativa para '{book_params['title']}'. Estilo artístico, colorido y educativo."
    )
    cover_path = os.path.join(output_dir, "cover.png")
    cover_image = generate_image(cover_prompt, cover_path)
    image_paths.append({"type": "cover", "path": cover_image})

    # Imágenes para cada capítulo
    chapters = book_content.get("chapters", [])
    for i, chapter in enumerate(chapters):
        chapter_title = chapter.get("title", f"Capítulo {i + 1}")
        chapter_prompt = generate_image_prompt(book_params, f"Ilustración para el capítulo: {chapter_title}")
        chapter_path = os.path.join(output_dir, f"chapter_{i + 1}.png")
        chapter_image = generate_image(chapter_prompt, chapter_path)
        image_paths.append({"type": "chapter", "path": chapter_image})

    return image_paths
