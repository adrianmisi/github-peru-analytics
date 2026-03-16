import os
import json
import csv
import time
from pathlib import Path
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from dotenv import load_dotenv

load_dotenv()

# Categorías basadas estrictamente en la CIIU (Categorías A - U)
PERU_INDUSTRIES = [
    "A - Agricultura, ganadería, silvicultura y pesca",
    "B - Explotación de minas y canteras",
    "C - Industrias manufactureras",
    "D - Suministro de electricidad, gas, vapor y aire acondicionado",
    "E - Suministro de agua; alcantarillado, gestión de desechos y actividades de saneamiento",
    "F - Construcción",
    "G - Comercio al por mayor y al por menor; reparación de vehículos automotores y motocicletas",
    "H - Transporte y almacenamiento",
    "I - Actividades de alojamiento y de servicio de comidas",
    "J - Información y comunicación",
    "K - Actividades financieras y de seguros",
    "L - Actividades inmobiliarias",
    "M - Actividades profesionales, científicas y técnicas",
    "N - Actividades de servicios administrativos y de apoyo",
    "O - Administración pública y defensa; planes de seguridad social de afiliación obligatoria",
    "P - Enseñanza",
    "Q - Actividades de atención de la salud humana y de asistencia social",
    "R - Actividades artísticas, de entretenimiento y recreativas",
    "S - Otras actividades de servicios",
    "T - Actividades de los hogares como empleadores",
    "U - Actividades de organizaciones y órganos extraterritoriales",
    "Desconocido" # En caso que el repositorio sea un fork o no tenga nada de info
]

class IndustryClassifier:
    """Clase encargada de usar GPT-4 para clasificar repositorios en base a rubros económicos."""
    
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Se requiere una API Key de OpenAI.")
            
        self.client = OpenAI(api_key=self.api_key)
        self.system_prompt = f"""
Eres un analista experto de la industria tecnológica de Perú. 
Tu tarea es analizar un repositorio de GitHub (su nombre, descripción, y contenido del README) e identificar a cuál de las 21 categorías económicas establecidas por el CIIU de Perú (Clasificación Industrial Internacional Uniforme) pertenece o está brindando sus servicios el software creado.

Estas son las categorías válidas obligatorias:
{json.dumps(PERU_INDUSTRIES, indent=2, ensure_ascii=False)}

REGLAS ESTRICTAS:
1. DEBES retornar únicamente un JSON válido, sin delimitadores de código markdown (```json).
2. El JSON debe tener exactamente esta estructura:
{{
  "category": "Una de las strings exactas de la lista provista arriba",
  "confidence": <número entre 0.0 y 1.0 indicando qué tan seguro estás>,
  "reasoning": "Un par de oraciones breves explicando por qué seleccionaste la categoría en base al código/descripción"
}}
3. Si el repositorio es puramente técnico o librerías (ej. React, parsers locales, dotfiles, configuración de OS) sin una industria clara, clasifícalo en "J - Información y comunicación" o "M - Actividades profesionales, científicas y técnicas".
4. Si es un proyecto universitario, pertenece a "P - Enseñanza".
5. Si no hay absolutamente nada que deducir o está vacío, usa "Desconocido".
"""

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        # reintentamos si OpenAI falla (ratelimit o error de servidor)
        retry=retry_if_exception_type(Exception)
    )
    def classify_repository(self, repo_name, description, readme_preview):
        """Llama a OpenAI para clasificar un repositorio dado su contexto."""
        repo_context = f"Repo Name: {repo_name}\nDescription: {description}\nREADME Snippet:\n{readme_preview}"
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",  # Usando el modelo especificado o fallback a gpt-4o
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": repo_context}
                ],
                temperature=0.1,  # Bajo para mayor determinismo y apego al JSON
                response_format={ "type": "json_object" } # Validamos la salida puramente JSON
            )
            
            result_str = response.choices[0].message.content
            return json.loads(result_str)
            
        except json.JSONDecodeError:
            return {"category": "Desconocido", "confidence": 0, "reasoning": "Error parseando JSON de OpenAI"}
        except Exception as e:
            print(f"Error clasificando repo '{repo_name}': {type(e).__name__} - {e}")
            raise e
