import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Agregar src a path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from app.utils.data_loader import load_all_data

st.set_page_config(page_title="Repository Browser", page_icon="📦", layout="wide")
st.title("📦 Repository Browser")

# Cargar Datos
with st.spinner('Cargando repositorio maestro...'):
    _, repos_df, classifications_df, _, _ = load_all_data()

if repos_df.empty or classifications_df.empty:
    st.warning("⚠️ No se encontraron repositorios o sus clasificaciones. Ejecute el recolector y clasificador primero.")
    st.stop()

st.markdown("""
Explora los +1000 proyectos de software minados de Perú. Cada repositorio incluye su industria predicha por **GPT-4** y las razones de dicha predicción.
""")

# Merge ambos DataFrames (repos + classifications)
# Preparando la llave para merge: owner + name
repos_df['repo_key'] = repos_df['owner'] + "/" + repos_df['name']
classifications_df['repo_key'] = classifications_df['owner'] + "/" + classifications_df['name']

master_df = pd.merge(repos_df, classifications_df[['repo_key', 'industry', 'confidence', 'reasoning']], on='repo_key', how='left')
master_df['industry'] = master_df['industry'].fillna('Desconocido')

# Filtros
col1, col2, col3 = st.columns(3)

with col1:
    search_query = st.text_input("🔍 Buscar por nombre o descripción:", "")

with col2:
    industry_filter = st.selectbox(
        "🏭 Filtrar por Sector Industrial:",
        options=["Todos"] + sorted(list(master_df['industry'].unique())),
        index=0
    )

with col3:
    lang_filter = st.text_input("💻 Filtrar por Lenguaje (ej. Python, TypeScript):", "")

# Aplicamos los filtros
filtered_df = master_df.copy()

if search_query:
    filtered_df = filtered_df[
        filtered_df['name'].str.contains(search_query, case=False, na=False) | 
        filtered_df['description'].str.contains(search_query, case=False, na=False)
    ]

if industry_filter != "Todos":
    filtered_df = filtered_df[filtered_df['industry'] == industry_filter]

if lang_filter:
    filtered_df = filtered_df[filtered_df['languages'].str.contains(lang_filter, case=False, na=False)]

# Ordenamos por cantidad de estrellas x defecto
filtered_df['stars'] = pd.to_numeric(filtered_df['stars'], errors='coerce').fillna(0)
filtered_df = filtered_df.sort_values(by='stars', ascending=False)

st.divider()
st.subheader(f"Mostrando {len(filtered_df)} Repositorios")

# Diseño en tabla custom para presentar razonamientos largos
for _, row in filtered_df.head(50).iterrows(): # Paginamos virtualmente a 50 para rendimiento UI
    with st.expander(f"⭐ {int(row['stars'])} | 📦 {row['repo_key']}"):
        st.markdown(f"**URL:** [https://github.com/{row['repo_key']}](https://github.com/{row['repo_key']})")
        desc = row.get("description", "Sin descripción.")
        st.markdown(f"**Descripción:** {desc if pd.notna(desc) else 'No disponible'}")
        
        c1, c2 = st.columns([1, 2])
        with c1:
            st.info(f"**Industria (AI):**\n\n{row.get('industry', 'Desconocido')}")
            st.metric("AI Confidence", f"{row.get('confidence', 0)} / 1.0")
            
        with c2:
            st.success(f"**Chat-GPT Reasoning:**\n\n{row.get('reasoning', 'No rationale provided')}")
            st.caption(f"Lenguajes extraídos desde el API: {row.get('languages', '{}')}")

if len(filtered_df) > 50:
    st.info(" Mostrando los primeros 50 resultados más estrellados. Refine los filtros para encontrar más.")
