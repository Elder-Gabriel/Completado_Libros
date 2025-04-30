USER_PROMPT_TEMPLATE = """
Eres un generador de libros educativos. Crea un libro titulado '{title}' para público {audience}, edades {age_range}, con {pages} páginas. 
Incluye introducción, varios capítulos, ejercicios de repaso y bibliografía.

El libro debe ser informativo, atractivo y adecuado para la edad del público objetivo.
Incluye datos precisos, ejemplos claros y un lenguaje apropiado para el rango de edad.

Estructura el libro de la siguiente manera:
1. Portada con título y breve descripción
2. Índice detallado
3. Introducción (1 página)
4. Contenido dividido en capítulos (80% de las páginas)
5. Ejercicios interactivos y de repaso (10% de las páginas)
6. Conclusión (1 página)
7. Bibliografía y recursos adicionales (1 página)

Devuelve el contenido en formato JSON con la siguiente estructura:
{{
  "title": "Título del libro",
  "description": "Breve descripción",
  "toc": {{"Capítulo 1": "página 3", ...}},
  "introduction": "Texto de introducción...",
  "chapters": [
    {{"title": "Título del capítulo 1", "content": "Contenido del capítulo 1..."}},
    ...
  ],
  "exercises": [
    {{"title": "Ejercicio 1", "description": "Descripción del ejercicio 1..."}},
    ...
  ],
  "conclusion": "Texto de conclusión...",
  "bibliography": ["Referencia 1", "Referencia 2", ...]
}}
"""

IMAGE_PROMPT_TEMPLATE = """
Genera una ilustración detallada para un libro educativo titulado '{title}' dirigido a {audience} de {age_range} años.
La imagen debe ilustrar: {description}
Estilo: Apropiado para niños, colorido, educativo y atractivo visualmente.
"""