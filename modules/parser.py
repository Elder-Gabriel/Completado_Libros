import json
import logging
from prompts.user_prompt import USER_PROMPT_TEMPLATE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_user_prompt(raw_prompt: str) -> dict:
    """
    Parsea el prompt del usuario en formato JSON y valida los campos requeridos.
    
    Args:
        raw_prompt (str): Prompt del usuario en formato JSON
    
    Returns:
        dict: Diccionario con los parámetros del libro
    """
    try:
        # Intentar parsear el JSON
        data = json.loads(raw_prompt)

        # Campos requeridos (eliminamos 'pages')
        required_fields = ['title', 'audience', 'age_range']
        for field in required_fields:
            if field not in data:
                raise ValueError(f"❌ El campo obligatorio '{field}' no está presente.")

        # Validaciones de tipo
        if not isinstance(data['title'], str):
            raise TypeError("❌ El campo 'title' debe ser una cadena de texto.")
        if not isinstance(data['audience'], str):
            raise TypeError("❌ El campo 'audience' debe ser una cadena de texto.")
        if not isinstance(data['age_range'], str):
            raise TypeError("❌ El campo 'age_range' debe ser una cadena de texto.")

        # Eliminamos la validación del número de páginas

        logger.info(f"✅ Prompt parseado correctamente: {data}")
        return data

    except json.JSONDecodeError as e:
        logger.error(f"❌ JSON inválido: {str(e)}")
        raise ValueError("El prompt debe estar en formato JSON válido.")
    except Exception as e:
        logger.error(f"❌ Error al procesar el prompt: {str(e)}")
        raise