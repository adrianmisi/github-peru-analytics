import streamlit as st
import pandas as pd
import sys
from pathlib import Path

# Agregar src a path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from app.utils.data_loader import load_all_data

st.set_page_config(page_title="Developer Explorer", page_icon="🧑‍💻", layout="wide")
st.title("🧑‍💻 Developer Explorer")

# Cargar Datos
with st.spinner('Cargando métricas de desarrolladores...'):
    _, _, _, user_metrics_df, _ = load_all_data()

if user_metrics_df.empty:
    st.warning("⚠️ No se encontraron métricas de desarrolladores.")
    st.stop()

st.markdown("""
Explora el ecosistema de desarrolladores Peruanos. Filtra por industria, actividad y visualiza sus métricas de impacto calculadas usando el framework base.
""")

# Filtros
col1, col2, col3 = st.columns(3)

with col1:
    industry_filter = st.selectbox(
        "Filtrar por Industria Dominante",
        options=["All"] + sorted(list(user_metrics_df['primary_industry'].dropna().unique())),
        index=0
    )

with col2:
    min_activity = st.slider(
        "Mínimo de Repositorios (Activity Score)",
        min_value=int(user_metrics_df['activity_repos'].min()),
        max_value=int(user_metrics_df['activity_repos'].max()),
        value=0
    )

with col3:
    sort_by = st.selectbox(
        "Ordernar por",
        options=["Influence (Stars+Followers)", "Activity (Repos)", "Technical (Languages)", "Engagement (Forks)"]
    )

# Aplicar Filtros
filtered_df = user_metrics_df.copy()

if industry_filter != "All":
    filtered_df = filtered_df[filtered_df['primary_industry'] == industry_filter]

filtered_df = filtered_df[filtered_df['activity_repos'] >= min_activity]

# Mappear sort logic
sort_col_map = {
    "Influence (Stars+Followers)": "influence_score",
    "Activity (Repos)": "activity_repos",
    "Technical (Languages)": "technical_languages",
    "Engagement (Forks)": "engagement_forks"
}

filtered_df = filtered_df.sort_values(by=sort_col_map[sort_by], ascending=False)

# Mostrar Tabla Interactiva
st.divider()
st.subheader(f"Encontrados: {len(filtered_df)} Desarrolladores")

display_cols = ['login', 'name', 'company', 'location', 'activity_repos', 'influence_score', 'technical_languages', 'engagement_forks', 'primary_industry']
st.dataframe(
    filtered_df[display_cols],
    use_container_width=True,
    hide_index=True,
    column_config={
        "login": st.column_config.TextColumn("GitHub Username", help="User handle de Github"),
        "name": st.column_config.TextColumn("Name"),
        "influence_score": st.column_config.NumberColumn("Influence ⭐", format="%d"),
        "activity_repos": st.column_config.NumberColumn("Activity 📦"),
        "technical_languages": st.column_config.NumberColumn("Tech Score 💻"),
        "engagement_forks": st.column_config.NumberColumn("Engagement 🚀"),
        "primary_industry": st.column_config.TextColumn("Industry 🏭")
    }
)

st.markdown("---")
st.markdown("*Las métricas son calculadas en base a sus contribuciones y repositorios no-forkeados públicos.*")
