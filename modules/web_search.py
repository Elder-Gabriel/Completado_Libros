import requests
import logging
from config import DUCKDUCKGO_SEARCH_URL

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def search_topic(query: str, max_results: int = 10) -> str:
    """
    Busca información sobre un tema utilizando la API de DuckDuckGo y la enriquece para su uso en generación de contenido.

    Args:
        query (str): Tema a buscar
        max_results (int): Número máximo de resultados a procesar
    
    Returns:
        str: Información ampliada sobre el tema
    """
    try:
        search_url = DUCKDUCKGO_SEARCH_URL.format(query)
        logger.info(f"Buscando información sobre: {query}")
        
        response = requests.get(search_url)
        if response.status_code != 200:
            logger.warning(f"Error al buscar información. Código: {response.status_code}")
            return f"No se encontró información confiable sobre {query}."

        try:
            data = response.json()
        except Exception as e:
            logger.warning(f"Error al parsear JSON: {str(e)}")
            return f"No se pudo interpretar la información sobre {query}."

        results = []

        # Abstract
        if data.get("Abstract"):
            results.append(f"{data['Abstract']}")

        # Definition
        if data.get("Definition"):
            results.append(f"{data['Definition']}")

        # Expandir RelatedTopics
        if data.get("RelatedTopics"):
            topics = data["RelatedTopics"]
            count = 0
            for topic in topics:
                if "Text" in topic:
                    results.append(topic["Text"])
                    count += 1
                elif "Topics" in topic:  # algunos vienen anidados
                    for sub in topic["Topics"]:
                        if "Text" in sub:
                            results.append(sub["Text"])
                            count += 1
                if count >= max_results:
                    break

        if not results:
            logger.warning(f"No se encontró información para: {query}")
            return f"Este tema, {query}, es importante pero actualmente no se dispone de suficiente información detallada."

        # Unir y expandir contenido
        joined_text = "\n".join(results)
        expanded = f"A continuación se presenta un resumen sobre el tema '{query}':\n\n{joined_text}\n\nEsta información sirve como base para desarrollar un contenido más profundo y educativo sobre el tema."

        logger.info(f"Contenido generado de búsqueda para: {query}")
        return expanded

    except Exception as e:
        logger.error(f"Fallo en búsqueda: {str(e)}")
        return f"Hubo un error al buscar información sobre {query}."
