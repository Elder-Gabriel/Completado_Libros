import os
import json
import logging
import openai
from user_prompt import USER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

def generate_book_content(book_params):
    """
    Genera el contenido del libro utilizando la API de OpenAI basado en los parámetros proporcionados.
    
    Args:
        book_params (dict): Parámetros del libro (título, tema, público, edad, etc.)
        
    Returns:
        dict: Contenido estructurado del libro en formato JSON
    """
    try:
        logger.info("🤖 Conectando con la API para generar contenido...")
        
        # Verificar que tenemos la clave API
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("No se encontró la clave API de OpenAI en las variables de entorno")
        
        client = openai.OpenAI(api_key=api_key)
        
        # Preparar el prompt para la API
        prompt = USER_PROMPT_TEMPLATE.format(
            title=book_params["title"],
            tema=book_params["tema"],
            publico=book_params["publico"],
            edad=book_params["edad"],
            nivel_academico=book_params["nivel_academico"],
            enfoque=book_params["enfoque"],
            formato_idioma=book_params["formato_idioma"],
            paginas_deseadas=book_params["paginas_deseadas"],
            profundidad=book_params["profundidad"]
        )
        
        logger.debug(f"📝 Prompt generado: {prompt[:100]}...")
        
        # Llamar a la API de OpenAI
        response = client.chat.completions.create(
            model="gpt-4o",  # Usar el modelo más avanzado disponible
            messages=[
                {"role": "system", "content": "Eres un experto generador de libros educativos detallados y profesionales."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=4000,
            response_format={"type": "json_object"}
        )
        
        # Extraer el contenido JSON de la respuesta
        content_text = response.choices[0].message.content
        logger.debug(f"📥 Respuesta recibida: {len(content_text)} caracteres")
        
        # Parsear el JSON
        try:
            book_content = json.loads(content_text)
            logger.info("✅ Contenido del libro generado y procesado exitosamente")
            
            # Verificar que todos los campos necesarios estén presentes
            required_fields = ["title", "description", "toc", "introduction", "chapters", "exercises", "conclusion", "bibliography"]
            for field in required_fields:
                if field not in book_content:
                    logger.warning(f"⚠️ Campo faltante en el contenido: {field}")
                    if field == "chapters":
                        book_content[field] = [{"title": "Capítulo por defecto", "content": "Contenido por defecto."}]
                    elif field == "exercises":
                        book_content[field] = [{"title": "Ejercicio por defecto", "description": "Descripción por defecto."}]
                    elif field == "bibliography":
                        book_content[field] = ["Referencia por defecto"]
                    else:
                        book_content[field] = "Contenido por defecto para " + field
            
            # Verificar campos adicionales específicos para EPUB
            additional_fields = ["tema", "publico", "edad", "nivel_academico", "enfoque", "formato_idioma", "profundidad"]
            for field in additional_fields:
                if field not in book_content and field in book_params:
                    book_content[field] = book_params[field]
            
            return book_content
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Error al parsear JSON: {str(e)}")
            logger.debug(f"Contenido que causó el error: {content_text}")
            
            # Crear una estructura mínima para evitar fallos completos
            return {
                "title": book_params["title"],
                "description": f"Libro sobre {book_params['tema']} para {book_params['publico']} de {book_params['edad']} años.",
                "tema": book_params["tema"],
                "publico": book_params["publico"],
                "edad": book_params["edad"],
                "nivel_academico": book_params["nivel_academico"],
                "enfoque": book_params["enfoque"],
                "formato_idioma": book_params["formato_idioma"],
                "profundidad": book_params["profundidad"],
                "toc": {"Capítulo 1": "página 3"},
                "introduction": "Introducción por defecto debido a un error en la generación.",
                "chapters": [{"title": "Capítulo 1", "content": "Contenido por defecto debido a un error en la generación."}],
                "exercises": [{"title": "Ejercicio 1", "description": "Descripción por defecto."}],
                "conclusion": "Conclusión por defecto.",
                "bibliography": ["Referencia por defecto"]
            }
    
    except Exception as e:
        logger.exception(f"❌ Error al generar contenido: {str(e)}")
        raise