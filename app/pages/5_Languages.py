import streamlit as st
import pandas as pd
import json
import plotly.express as px
from collections import defaultdict
import sys
from pathlib import Path

# Agregar src a path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from app.utils.data_loader import load_all_data

st.set_page_config(page_title="Language Analytics", page_icon="💻", layout="wide")
st.title("💻 Language Analytics")

# Cargar Datos
with st.spinner('Procesando bytes y lenguajes...'):
    users_df, repos_df, classifications_df, _, _ = load_all_data()

if repos_df.empty:
    st.warning("⚠️ Sin datos de repositorios para calcular lenguajes.")
    st.stop()

st.markdown("""
Analítica profunda de los lenguajes de programación, frameworks de datos y lenguajes de marcado utilizados en el territorio nacional. Cifras minadas usando las APIs lingüísticas y transformadas de Bytes a MB.
""")

# Procesado dinámico al vuelo de todos los lenguajes por si cambian los datos
lang_bytes = defaultdict(int)
lang_repos_count = defaultdict(int)

# Para cruzar lenguajes x industria
repo_industry_map = {}
for _, cl in classifications_df.iterrows():
    repo_industry_map[f"{cl['owner']}/{cl['name']}"] = cl['industry']

# Estructura {Industria: {Lenguaje: Bytes}}
industry_lang_bytes = defaultdict(lambda: defaultdict(int))

for _, repo in repos_df.iterrows():
    try:
        langs = json.loads(repo.get('languages_bytes', '{}'))
        repo_key = f"{repo['owner']}/{repo['name']}"
        ind = repo_industry_map.get(repo_key, 'Desconocido')
        
        for lang, count in langs.items():
            lang_bytes[lang] += count
            lang_repos_count[lang] += 1
            industry_lang_bytes[ind][lang] += count
    except:
        pass

# 1. Total bytes to DF
df_bytes = pd.DataFrame(list(lang_bytes.items()), columns=['Language', 'Bytes'])
df_bytes['MBs'] = df_bytes['Bytes'] / (1024 * 1024)
df_bytes = df_bytes.sort_values(by='MBs', ascending=False)

df_repos = pd.DataFrame(list(lang_repos_count.items()), columns=['Language', 'Repos Using It'])
df_repos = df_repos.sort_values(by='Repos Using It', ascending=False)

col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Lenguajes por Volumen (Código Válido Total en MB)")
    fig1 = px.bar(
        df_bytes.head(15), 
        x='Language', 
        y='MBs',
        color='MBs',
        color_continuous_scale='Inferno',
        text_auto='.2s'
    )
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Adopción: % de Repositorios que incluyen el lenguaje")
    # Limitar a top 15 más ubicuos
    top15_ub = df_repos.head(15).copy()
    top15_ub['Adoption %'] = (top15_ub['Repos Using It'] / len(repos_df)) * 100
    
    fig2 = px.bar(
        top15_ub,
        x='Language',
        y='Adoption %',
        color='Repos Using It',
        color_continuous_scale='aggrnyl',
        text_auto='.1f'
    )
    fig2.update_traces(textposition='outside')
    st.plotly_chart(fig2, use_container_width=True)


st.divider()
st.subheader("Uso de Lenguajes según la Industria (Matriz Térmica)")

# Preparar DF Heatmap
heat_data = []
for ind, langs in industry_lang_bytes.items():
    if ind == 'Desconocido':
        continue # Omitir unknown para ver claro las industrias reales
        
    for l, val in langs.items():
        heat_data.append({"Industry": ind, "Language": l, "MBs": val / (1024*1024)})

df_heat = pd.DataFrame(heat_data)
if not df_heat.empty:
    # Agrupar y filtrar los 20 top lenguajes y combinarlos
    top_global_langs = df_bytes.head(20)['Language'].tolist()
    df_heat = df_heat[df_heat['Language'].isin(top_global_langs)]

    fig_heat = px.density_heatmap(
        df_heat, 
        x='Language', 
        y='Industry', 
        z='MBs',
        histfunc="sum",
        color_continuous_scale='Viridis',
        title="Mapas de Calor: MBs de código escrito por industria target"
    )
    # Hacerlo más ancho para evitar encimar texto
    fig_heat.update_layout(height=600)
    st.plotly_chart(fig_heat, use_container_width=True)
else:
    st.info("Sin data industrial cruzada aún.")
