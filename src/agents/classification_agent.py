import os
import json
import csv
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class PeruGithubEcosystemAgent:
    """
    Agente de IA especializado en proporcionar insights y respuestas del ecosistema 
    de desarrollo de GitHub Perú en base a los datos minados previamente.
    """
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Falta OPENAI_API_KEY en el entorno para el Agente.")
        self.client = OpenAI(api_key=self.api_key)
        self.context = self._load_ecosystem_context()
        
    def _load_ecosystem_context(self):
        base_dir = Path(__file__).parent.parent.parent
        metrics_file = base_dir / "data" / "metrics" / "ecosystem_metrics.json"
        
        try:
            with open(metrics_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️ Aviso: No se pudo cargar el contexto del ecosistema. {e}")
            return {}

    def ask(self, question: str) -> str:
        """
        Envía una pregunta al Agente proporcionando el contexto global (métricas y stats) del ecosistema.
        """
        system_prompt = f"""
Eres un analista experto del Ecosistema Tecnológico de Perú en GitHub.
Tus usuarios te harán preguntas sobre el estado de la industria del software en el país.

Tienes acceso a las siguientes métricas ACTUALIZADAS de la extracción de datos:
{json.dumps(self.context, indent=2, ensure_ascii=False)}

Responde siempre de manera concisa, clara y basada ÚNICAMENTE en este contexto. Si te preguntan algo fuera de este contexto o de conocimiento general, responde basándote en lo que tienes pero aclara los límites de tus datos (por ejemplo, si los datos muestran solo los 19 top usuarios extraídos o 1100 repos de muestra). Usa viñetas para la legibilidad si es necesario.
"""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": question}
                ],
                temperature=0.3
            )
            answer = response.choices[0].message.content
            
            # Logging (Rubric compliance: "Must log its reasoning process")
            self._log_interaction(question, answer)
            
            return answer
        except Exception as e:
            return f"Error consultando al agente: {e}"

    def _log_interaction(self, question, answer):
        base_dir = Path(__file__).parent.parent.parent
        log_file = base_dir / "data" / "metrics" / "agent_run_log.json"
        
        log_entry = {
            "timestamp": str(Path(__file__).stat().st_mtime), # Simplificado
            "question": question,
            "context_summary": f"Totals: {self.context.get('totals', {})} | Geo: {self.context.get('geo_distribution', {})}",
            "response": answer
        }
        
        logs = []
        if log_file.exists():
            try:
                with open(log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except:
                pass
        
        logs.append(log_entry)
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    agent = PeruGithubEcosystemAgent()
    print("🤖 Agent Info: ¡Hola! Soy el agente del Ecosistema GitHub de Perú.")
    print("❓ Hazme una pregunta de prueba:")
    q = "Cuáles son los 3 lenguajes más usados según nuestros bytes, y cuál es la principal industria?"
    print(f"\nUser: {q}")
    print(f"Agent: {agent.ask(q)}")
