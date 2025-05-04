import os
import json
import logging
import requests
import time
import openai
from user_prompt import IMAGE_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

def generate_image_prompt(book_params, description):
    """
    Genera un prompt detallado para la creación de imágenes.
    
    Args:
        book_params (dict): Parámetros del libro
        description (str): Descripción específica para la imagen
        
    Returns:
        str: Prompt para generar la imagen
    """
    # Adaptar el estilo según el público y edad
    prompt = IMAGE_PROMPT_TEMPLATE.format(
        title=book_params["title"],
        publico=book_params["publico"],
        edad=book_params["edad"],
        tema=book_params["tema"],
        nivel_academico=book_params["nivel_academico"],
        enfoque=book_params["enfoque"],
        description=description
    )
    
    # Añadir especificaciones técnicas si el tema lo requiere
    if any(term in book_params["tema"].lower() for term in ["matemáticas", "programación", "ciencia", "física", "química", "biología"]):
        prompt += "\nEstilo técnico: Incluye diagramas claros, etiquetas precisas y representaciones visuales exactas."
    
    # Adaptar estilo según edad
    try:
        edad_min = int(book_params["edad"].split("-")[0])
        if edad_min < 12:
            prompt += "\nEstilo: Colorido, amigable, con personajes y elementos visuales atractivos para niños."
        elif edad_min < 18:
            prompt += "\nEstilo: Moderno, dinámico, con elementos gráficos atractivos para adolescentes."
        else:
            prompt += "\nEstilo: Profesional, sobrio, con visualizaciones claras y enfoque en la información."
    except (ValueError, IndexError):
        # Si no se puede determinar la edad, usar un estilo neutro
        prompt += "\nEstilo: Equilibrado entre visual y profesional, adaptado al contenido educativo."
    
    return prompt

def generate_images_dalle(prompts, images_dir, quality="standard"):
    """
    Genera imágenes utilizando DALL-E de OpenAI.
    
    Args:
        prompts (list): Lista de prompts para generar imágenes
        images_dir (str): Directorio donde guardar las imágenes
        quality (str): Calidad de las imágenes ('standard' o 'hd')
        
    Returns:
        list: Información sobre las imágenes generadas
    """
    image_info = []
    
    try:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("No se encontró la clave API de OpenAI en las variables de entorno")
        
        client = openai.OpenAI(api_key=api_key)
        
        for i, prompt in enumerate(prompts):
            try:
                logger.info(f"🎨 Generando imagen {i+1}/{len(prompts)}")
                
                response = client.images.generate(
                    model="dall-e-3",  # Usar el modelo más avanzado disponible
                    prompt=prompt,
                    size="1024x1024",
                    quality=quality,
                    n=1,
                )
                
                image_url = response.data[0].url
                
                # Descargar la imagen
                image_path = os.path.join(images_dir, f"image_{i+1}.png")
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                
                response = requests.get(image_url)
                with open(image_path, "wb") as f:
                    f.write(response.content)
                
                # Registrar información de la imagen
                image_info.append({
                    "path": image_path,
                    "prompt": prompt,
                    "description": f"Imagen {i+1} para el libro"
                })
                
                logger.info(f"✅ Imagen {i+1} guardada en: {image_path}")
                
                # Esperar un poco entre solicitudes para evitar límites de tasa
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"❌ Error al generar imagen {i+1}: {str(e)}")
                continue
    
    except Exception as e:
        logger.exception(f"❌ Error general en la generación de imágenes: {str(e)}")
    
    return image_info

def generate_images_fallback(descriptions, images_dir):
    """
    Método alternativo para obtener imágenes cuando no se puede usar DALL-E.
    Usa imágenes de placeholder o imágenes libres de derechos.
    
    Args:
        descriptions (list): Lista de descripciones para las imágenes
        images_dir (str): Directorio donde guardar las imágenes
        
    Returns:
        list: Información sobre las imágenes generadas
    """
    image_info = []
    
    try:
        # URLs de algunas imágenes de placeholder
        placeholder_urls = [
            "https://via.placeholder.com/800x600.png?text=Imagen+Educativa+1",
            "https://via.placeholder.com/800x600.png?text=Imagen+Educativa+2",
            "https://via.placeholder.com/800x600.png?text=Imagen+Educativa+3",
            "https://via.placeholder.com/800x600.png?text=Imagen+Educativa+4",
            "https://via.placeholder.com/800x600.png?text=Imagen+Educativa+5"
        ]
        
        # Usar solo la cantidad necesaria de URLs
        urls_to_use = placeholder_urls[:min(len(descriptions), len(placeholder_urls))]
        
        for i, (url, desc) in enumerate(zip(urls_to_use, descriptions)):
            try:
                # Descargar la imagen
                image_path = os.path.join(images_dir, f"image_{i+1}.png")
                os.makedirs(os.path.dirname(image_path), exist_ok=True)
                
                response = requests.get(url)
                with open(image_path, "wb") as f:
                    f.write(response.content)
                
                # Registrar información de la imagen
                image_info.append({
                    "path": image_path,
                    "description": desc
                })
                
                logger.info(f"✅ Imagen placeholder {i+1} guardada en: {image_path}")
                
            except Exception as e:
                logger.error(f"❌ Error al descargar imagen placeholder {i+1}: {str(e)}")
                continue
    
    except Exception as e:
        logger.exception(f"❌ Error general en la generación de imágenes fallback: {str(e)}")
    
    return image_info

def generate_book_images(book_content, book_params, images_dir):
    """
    Genera imágenes para el libro basado en su contenido.
    
    Args:
        book_content (dict): Contenido del libro en formato JSON
        book_params (dict): Parámetros del libro
        images_dir (str): Directorio donde guardar las imágenes
        
    Returns:
        dict: Información sobre las imágenes generadas, organizada por capítulos
    """
    try:
        os.makedirs(images_dir, exist_ok=True)
        logger.info(f"📁 Directorio de imágenes creado: {images_dir}")
        
        images_info = {}
        
        # Generar imagen de portada
        cover_prompt = generate_image_prompt(
            book_params, 
            f"Portada del libro '{book_content['title']}'. Representación visual del tema principal: {book_params['tema']}"
        )
        cover_prompts = [cover_prompt]
        
        # Generar prompts para imágenes de capítulos
        chapter_prompts = []
        chapter_descriptions = []
        
        for i, chapter in enumerate(book_content["chapters"], 1):
            # Extraer conceptos clave del capítulo
            chapter_text = chapter["content"]
            chapter_title = chapter["title"]
            
            # Limitar a 500 caracteres para el prompt
            short_content = chapter_text[:500] + "..." if len(chapter_text) > 500 else chapter_text
            
            # Crear un prompt específico para este capítulo
            chapter_prompt = generate_image_prompt(
                book_params,
                f"Ilustración para el capítulo '{chapter_title}'. Contenido: {short_content}"
            )
            
            chapter_prompts.append(chapter_prompt)
            chapter_descriptions.append(f"Ilustración del capítulo: {chapter_title}")
        
        # Intentar generar imágenes con DALL-E
        try:
            # Primero la portada
            cover_images = generate_images_dalle(cover_prompts, images_dir, quality="hd")
            if cover_images:
                images_info["cover"] = cover_images
            
            # Luego los capítulos
            chapter_images = generate_images_dalle(chapter_prompts, images_dir)
            
            # Organizar las imágenes por capítulos
            for i, img_info in enumerate(chapter_images):
                chapter_key = f"chapter_{i+1}"
                if chapter_key not in images_info:
                    images_info[chapter_key] = []
                images_info[chapter_key].append(img_info)
        
        except Exception as e:
            logger.warning(f"⚠️ No se pudieron generar imágenes con DALL-E: {str(e)}")
            logger.info("🔄 Usando método alternativo para obtener imágenes...")
            
            # Si falla DALL-E, usar imágenes de placeholder
            all_descriptions = ["Portada del libro"] + chapter_descriptions
            all_images = generate_images_fallback(all_descriptions, images_dir)
            
            # Asignar imágenes a capítulos
            if all_images:
                # Portada
                if len(all_images) > 0:
                    images_info["cover"] = [all_images[0]]
                
                # Capítulos
                for i, img_info in enumerate(all_images[1:], 1):
                    chapter_key = f"chapter_{i}"
                    if chapter_key not in images_info:
                        images_info[chapter_key] = []
                    images_info[chapter_key].append(img_info)
        
        logger.info(f"🖼️ Total de imágenes generadas: {sum(len(imgs) for imgs in images_info.values())}")
        return images_info
    
    except Exception as e:
        logger.exception(f"❌ Error general en la generación de imágenes: {str(e)}")
        # Devolver un diccionario vacío en caso de error
        return {}