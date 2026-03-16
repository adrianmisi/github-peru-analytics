import streamlit as st
from pathlib import Path

# Configuración inicial (Debe ser la primera llamada en Streamlit)
st.set_page_config(
    page_title="GitHub Peru Analytics",
    page_icon="🇵🇪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Definir la estructura de navegación de páginas usando multipage de Streamlit (st.Page desde st 1.36+)
pages = {
    "Dashboards": [
        st.Page("pages/1_Overview.py", title="Overview", icon="📊", default=True),
        st.Page("pages/2_Developers.py", title="Developer Explorer", icon="🧑‍💻"),
        st.Page("pages/3_Repositories.py", title="Repository Browser", icon="📦"),
    ],
    "Análisis Avanzado": [
        st.Page("pages/4_Industries.py", title="Industry Analysis", icon="🏭"),
        st.Page("pages/5_Languages.py", title="Language Analytics", icon="💻"),
        st.Page("pages/6_AI_Agent.py", title="AI Ecosystem Agent", icon="🤖"),
    ]
}


pg = st.navigation(pages)

# Mostrar la barra superior y navegación
st.sidebar.markdown("""
### 🇵🇪 GitHub Peru Analytics
Plataforma de análisis de la industria del software y desarrolladores en el Perú. 
Minería de datos realizada utilizando la GitHub REST API y ChatGPT.
""")

st.logo("https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png", icon_image="https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png")

# Ejecutar la página seleccionada
pg.run()
