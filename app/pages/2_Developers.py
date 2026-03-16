import streamlit as st
import pandas as pd
import plotly.express as px
import sys
from pathlib import Path

# Agregar src a path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from app.utils.data_loader import load_all_data

st.set_page_config(page_title="Developer Explorer", page_icon="🧑‍💻", layout="wide")
st.title("🧑‍💻 Talent Analytics & Developer Explorer")

# Cargar Datos
with st.spinner('Cargando métricas de desarrolladores...'):
    _, _, _, user_metrics_df, _ = load_all_data()

if user_metrics_df.empty:
    st.warning("⚠️ No se encontraron métricas de desarrolladores.")
    st.stop()

st.markdown("""
Análisis de talento del ecosistema Peruano. Esta sección clasifica a los desarrolladores en **Clústers** según su impacto y actividad técnica.
""")

# 1. Clustering Visualization
st.subheader("Talent Clustering (Influence vs Activity)")
fig_cluster = px.scatter(
    user_metrics_df,
    x="activity_repos",
    y="influence_score",
    color="developer_cluster",
    size="technical_languages",
    hover_name="login",
    text="login",
    labels={
        "activity_repos": "Activity (Public Repos)",
        "influence_score": "Influence (Stars + Followers)",
        "developer_cluster": "Talent Cluster",
        "technical_languages": "Tech Score"
    },
    title="Developer Landscape: Impact vs Quantity",
    color_discrete_sequence=px.colors.qualitative.Prism
)
fig_cluster.update_traces(textposition='top center')
st.plotly_chart(fig_cluster, use_container_width=True)

st.divider()

# 2. Explorer with Filters
st.subheader("🔎 Advanced Developer Search")

col1, col2, col3 = st.columns(3)

with col1:
    cluster_filter = st.multiselect(
        "Filtrar por Clúster",
        options=sorted(user_metrics_df['developer_cluster'].unique()),
        default=sorted(user_metrics_df['developer_cluster'].unique())
    )

with col2:
    min_activity = st.slider(
        "Mínimo de Repositorios",
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
filtered_df = filtered_df[filtered_df['developer_cluster'].isin(cluster_filter)]
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
st.caption(f"Encontrados: {len(filtered_df)} Desarrolladores")

display_cols = ['login', 'developer_cluster', 'activity_repos', 'influence_score', 'technical_languages', 'engagement_forks', 'primary_industry', 'location']
st.dataframe(
    filtered_df[display_cols],
    use_container_width=True,
    hide_index=True,
    column_config={
        "login": st.column_config.TextColumn("GitHub Username"),
        "developer_cluster": st.column_config.TextColumn("Talent Cluster 🏆"),
        "influence_score": st.column_config.NumberColumn("Influence ⭐", format="%d"),
        "activity_repos": st.column_config.NumberColumn("Activity 📦"),
        "technical_languages": st.column_config.NumberColumn("Tech Score 💻"),
        "engagement_forks": st.column_config.NumberColumn("Engagement 🚀"),
        "primary_industry": st.column_config.TextColumn("Industry 🏭")
    }
)

st.markdown("---")
st.caption("*Analysis based on public, non-forked repository metadata.*")

