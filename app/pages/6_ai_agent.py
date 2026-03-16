import streamlit as st
import sys
from pathlib import Path

# Agregar src a path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from src.agents.classification_agent import PeruGithubEcosystemAgent


st.set_page_config(page_title="AI Ecosystem Agent", page_icon="🤖", layout="wide")
st.title("🤖 Chat con el Ecosistema Peruanoh (AI Agent)")

st.markdown("""
Interactúa con nuestro agente experto en los datos recolectados. El agente tiene conocimiento total de las métricas agregadas más frescas (Lenguajes top, sectores industriales líderes y conteos de datos locales). ¡Pregúntale lo que quieras sobre el panorama tech actual del Perú usando RAG!
""")

# Lazy Initialization del agente en Streamlit State para no relogear
if "agent_instance" not in st.session_state:
    try:
        st.session_state.agent_instance = PeruGithubEcosystemAgent()
    except Exception as e:
        st.error(f"⚠️ Error iniciando el agente de ChatGPT: {e}. Verifique su OPENAI_API_KEY en el .env.")
        st.stop()

# Manejo de chat history en streamlit
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "¡Hola! Soy el AI Agent especialista en el Ecosystema de GitHub de Perú. Teniendo en cuenta la data recolectada hoy, ¿En qué te ayudo?"}
    ]

# Muestra historial de chat (UI)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Reacción a input de user
if prompt := st.chat_input("Ej: ¿Cuál es el sector donde los peruanos desarrollan más?"):
    # Agregar al UI user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Respuesta del bot
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        with st.spinner("🧠 El agente está analizando las métricas peruanas..."):
            response = st.session_state.agent_instance.ask(prompt)
            message_placeholder.markdown(response)
            
    # Subir al state
    st.session_state.messages.append({"role": "assistant", "content": response})

st.divider()
st.caption("Powered by **OpenAI gpt-4-turbo** y métricas minadas del REST y GraphQL API.")
