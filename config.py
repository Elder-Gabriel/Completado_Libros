import os
from dotenv import load_dotenv
import logging

# Configurar logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cargar variables de entorno desde .env
try:
    load_dotenv()
except Exception as e:
    logger.warning(f"No se pudo cargar el archivo .env: {str(e)}")

# Configuración de API
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.warning("No se encontró OPENAI_API_KEY en el archivo .env")

DUCKDUCKGO_SEARCH_URL = "https://api.duckduckgo.com/?q={}&format=json"

# Configuración de generación de contenido
GPT_MODEL = os.getenv("GPT_MODEL", "gpt-4")
IMAGE_SIZE = os.getenv("IMAGE_SIZE", "1024x1024")
IMAGES_FREQUENCY = int(os.getenv("IMAGES_FREQUENCY", "5"))  # Una imagen cada 5 páginas

# Configuración de PDF
PDF_MARGIN = 50
PDF_WIDTH = 595  # A4 width en puntos
PDF_HEIGHT = 842  # A4 height en puntos
FONT_SIZE_TITLE = 24
FONT_SIZE_HEADING = 18
FONT_SIZE_SUBHEADING = 14
FONT_SIZE_BODY = 12