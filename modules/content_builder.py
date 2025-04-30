import os
import logging
import openai
from modules.image_generator import generate_image, generate_image_prompt

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de la API de OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")

# Modelo a usar para generación de texto
MODEL = "gpt-4"

def generate_book_content(book_params: dict) -> dict:
    """
    Genera el contenido completo del libro (Introducción, 15 capítulos, Ejercicios, 
    Conclusión, Bibliografía) utilizando llamadas a la API de OpenAI.
    
    Args:
        book_params: Diccionario con parámetros del libro como:
            - title: Título del libro
            - audience: Público objetivo (niños, jóvenes, adultos)
            - age_range: Rango de edad del público
            
    Returns:
        dict: Diccionario con todo el contenido del libro estructurado
    """
    try:
        title = book_params.get("title", "Libro sin título")
        audience = book_params.get("audience", "general")
        age_range = book_params.get("age_range", "todas las edades")

        logger.info(f"Generando contenido para libro: '{title}' (Público: {audience}, Edad: {age_range})")

        # 1. Introducción
        intro_prompt = (
            f"Eres un escritor educativo. Genera una introducción de 2-3 párrafos para un libro titulado '{title}', "
            f"dirigido a {audience} de {age_range} años. Debe ser motivadora y presentar los temas que se abordarán."  
        )
        intro_resp = openai.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": intro_prompt}]
        )
        introduction = intro_resp.choices[0].message.content.strip()

        # 2. Generar 15 títulos de capítulos
        index_prompt = (
            f"Genera una lista numerada de 15 títulos de capítulos únicos para un libro sobre '{title}', "
            f"dirigido a {audience} de {age_range} años. Solo devuelve la lista."  
        )
        index_resp = openai.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": index_prompt}]
        )
        # Parsear títulos removiendo números
        raw_titles = index_resp.choices[0].message.content.strip().splitlines()
        chapter_titles = [line.split('. ', 1)[-1] for line in raw_titles if '. ' in line]

        # 3. Generar contenido para cada capítulo
        chapters = []
        for idx, chap_title in enumerate(chapter_titles, start=1):
            try:
                chap_prompt = (
                    f"Eres un escritor educativo. Escribe el contenido del capítulo '{chap_title}' para el libro '{title}', "
                    f"dirigido a {audience} de {age_range} años. Empieza con un breve párrafo introductorio y luego 3-4 párrafos "
                    f"de desarrollo con ejemplos y explicaciones claras."  
                )
                chap_resp = openai.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "user", "content": chap_prompt}]
                )
                chap_content = chap_resp.choices[0].message.content.strip()
                chapters.append({"title": f"Capítulo {idx}: {chap_title}", "content": chap_content})
            except Exception as e:
                logger.error(f"Error generando capítulo {idx}: {str(e)}")
                chapters.append({"title": f"Capítulo {idx}: {chap_title}", "content": "Error al generar contenido."})

        # 4. Generar ejercicios de repaso
        exer_prompt = (
            f"Crea 5 ejercicios de repaso para un libro sobre '{title}', dirigido a {audience} de {age_range} años. "
            "Incluye actividades prácticas, preguntas de reflexión y tareas de investigación."  
        )
        exer_resp = openai.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": exer_prompt}]
        )
        exercises = exer_resp.choices[0].message.content.strip()

        # 5. Generar conclusión
        concl_prompt = (
            f"Escribe una conclusión motivadora de 2 párrafos para un libro titulado '{title}', "
            f"dirigido a {audience} de {age_range} años, recalcando los puntos clave y llamando a la acción."  
        )
        concl_resp = openai.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": concl_prompt}]
        )
        conclusion = concl_resp.choices[0].message.content.strip()

        # 6. Generar bibliografía
        bib_prompt = (
            f"Proporciona una lista de 5 referencias bibliográficas confiables (libros, artículos o sitios web) "
            f"usadas en la creación del contenido sobre '{title}'."  
        )
        bib_resp = openai.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": bib_prompt}]
        )
        bibliography = bib_resp.choices[0].message.content.strip().splitlines()
        
        # Limpiar bibliografía de posibles numeraciones
        clean_bibliography = []
        for ref in bibliography:
            if '. ' in ref and ref[0].isdigit():
                clean_bibliography.append(ref.split('. ', 1)[-1])
            else:
                clean_bibliography.append(ref)

        # 7. Crear índice completo
        index_content = "\n".join(raw_titles)
        index_content += "\nEjercicios de repaso\nConclusión\nBibliografía"

        # 8. Ensamblar estructura final
        book_content = {
            "title": title,
            "introduction": introduction,
            "chapters": chapters,
            "index": index_content,
            "exercises": exercises,
            "conclusion": conclusion,
            "bibliography": clean_bibliography
        }

        return book_content
        
    except Exception as e:
        logger.error(f"Error generando contenido del libro: {str(e)}")
        return {
            "title": book_params.get("title", "Error"),
            "error": f"No se pudo generar el contenido del libro: {str(e)}"
        }