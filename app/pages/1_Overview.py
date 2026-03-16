import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

# Agregar src a path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from app.utils.data_loader import load_all_data, format_number

st.title("📊 Peru GitHub Ecosystem Overview")

# Cargar Datos
with st.spinner('Cargando datos del dataset...'):
    users_df, repos_df, classifications_df, user_metrics_df, eco_metrics = load_all_data()

if user_metrics_df.empty or not eco_metrics:
    st.warning("⚠️ No se encontraron datos procésados. Por favor ejecute la minería y procesamiento primero.")
    st.stop()

st.markdown("""
Bienvenido al dashboard interactivo del análisis de desarrolladores Peruanos.
Aquí se muestra una vista a alto nivel del impacto técnico del ecosistema de software a nivel nacional.
""")

# Top metrics - 4 columnas
st.divider()
st.subheader("High-Level Metrics")
c1, c2, c3, c4 = st.columns(4)

totals = eco_metrics.get("totals", {})
av_foll = eco_metrics.get("averages", {}).get("followers_per_user", 0)

c1.metric("👩‍💻 Total Developers", format_number(totals.get("users", len(users_df))))
c2.metric("📦 Extracted Repositories", format_number(totals.get("repositories", len(repos_df))))
c3.metric("🏭 Predicted Industries", format_number(totals.get("classifications", len(classifications_df))))
c4.metric("⭐ Avg Followers/Dev", f"{av_foll:.1f}")

st.divider()

# Charts
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Top Frameworks & Languages")
    # Limpiando la estructura de JSON y bytes devueltos
    top_langs = eco_metrics.get("top_languages_by_bytes", {})
    if top_langs:
        # Convertir bytes a MB
        langs_df = pd.DataFrame(list(top_langs.items()), columns=['Language', 'Bytes'])
        langs_df['MBs'] = langs_df['Bytes'] / (1024 * 1024)
        
        # Filtrar si hay muy pocos (nullos o Nones del backend)
        langs_df = langs_df[langs_df['Language'] != 'null']
        
        fig_lang = px.bar(
            langs_df.head(10), 
            x='MBs', 
            y='Language',
            orientation='h',
            title="Most Written Languages (in MB of total codebase)",
            color='MBs',
            color_continuous_scale="Viridis"
        )
        fig_lang.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_lang, use_container_width=True)

with col2:
    st.markdown("### Geographical Distribution")
    geo = eco_metrics.get("geo_distribution", {})
    if geo:
        geo_df = pd.DataFrame(list(geo.items()), columns=['Location', 'Count'])
        fig_geo = px.pie(
            geo_df, 
            values='Count', 
            names='Location',
            title="Developers Location Density",
            hole=0.4
        )
        st.plotly_chart(fig_geo, use_container_width=True)

st.markdown("### Impact By Industry (Top 10)")
top_inds = eco_metrics.get("top_industries_by_repo_count", {})
if top_inds:
    inds_df = pd.DataFrame(list(top_inds.items()), columns=['Industry', 'Repo Count'])
    # Remover el Desconocido para hacer gráficas bonitas
    inds_clean = inds_df[inds_df['Industry'] != 'Desconocido'].head(10)
    
    fig_ind = px.bar(
        inds_clean,
        x='Industry',
        y='Repo Count',
        title="Software Penetration by peruvian economic sectors (GPT-4 Classification)",
        color='Repo Count',
        color_continuous_scale="Blues"
    )
    # Acortar textos largos (X axis truncate)
    fig_ind.update_xaxes(tickangle=45, ticklen=5)
    st.plotly_chart(fig_ind, use_container_width=True)
