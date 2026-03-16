import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

# Agregar src a path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from app.utils.data_loader import load_all_data

# Página: Industry Analysis (Configurada vía main.py)
st.title("🏭 Industry Analysis")

# Cargar Datos
with st.spinner('Cargando modelos industriales...'):
    _, repos_df, classifications_df, user_metrics_df, _ = load_all_data()

if classifications_df.empty:
    st.warning("⚠️ Sin datos de clasificación disponibles.")
    st.stop()
    
st.markdown("""
Métricas detalladas del impacto del desarrollo de software en los diferentes sectores económicos del Perú. Datos deducidos por la inteligencia artificial sobre la descripción y el código de cada repositorio.
""")

st.divider()

# Preparar DF con las clasificaciones evitando NAs
valid_classifications = classifications_df[classifications_df['industry'] != 'Desconocido'].copy()

# 1. Total de Distribución Global
st.subheader("Distribución Global del Desarrollo (AI Classified)")

ind_counts = valid_classifications['industry'].value_counts().reset_index()
ind_counts.columns = ['Sector Industrial', 'Cantidad de Proyectos']

fig1 = px.pie(
    ind_counts, 
    values='Cantidad de Proyectos', 
    names='Sector Industrial',
    title="Participación por Sector Comercial (Proyectos Exitosos/Identificables)",
    hole=0.3
)
st.plotly_chart(fig1, use_container_width=True)

# 2. Análisis de Confianza del Modelo vs Industria
st.divider()
st.subheader("Confianza Promedio del Modelo Experto por Industria")
st.markdown("¿Qué tan seguro está GPT-4 de que los repositorios pertenecen al sector designado?")

# Preparamos data agregando el confidence
valid_classifications['confidence'] = pd.to_numeric(valid_classifications['confidence'], errors='coerce').fillna(0)
conf_aggs = valid_classifications.groupby('industry')['confidence'].mean().reset_index()
conf_aggs = conf_aggs.sort_values(by='confidence', ascending=False)

fig2 = px.bar(
    conf_aggs,
    x='confidence',
    y='industry',
    orientation='h',
    title="Nivel de Certeza del LLM (0-1.0) por Categoría Predicha",
    color='confidence',
    color_continuous_scale='Mint'
)
st.plotly_chart(fig2, use_container_width=True)

# 3. Desarrolladores predominantes por Industria  (Sacados de User Metrics)
st.divider()
st.subheader("Desarrolladores Dominantes por Industria")

if not user_metrics_df.empty:
    valid_devs = user_metrics_df[user_metrics_df['primary_industry'] != 'Desconocido']
    dev_counts = valid_devs['primary_industry'].value_counts().reset_index()
    dev_counts.columns = ['Sector', 'Developers Concentrados']
    
    fig3 = px.funnel(
        dev_counts, 
        x='Developers Concentrados', 
        y='Sector',
        title="Enfoque Primario de los Talentos Peruanos Minados (Funnel Analysis)"
    )
    st.plotly_chart(fig3, use_container_width=True)
else:
    st.info("Aún no se calcularon las métricas de usuario completas.")
    
st.markdown("---")
st.caption("Nota: Las industrias reflejadas son las 21 categorías propuestas por el Código CIIU, las cuales son ampliamente implementadas en clasificaciones del SUNAT/INEI en el Perú.")
