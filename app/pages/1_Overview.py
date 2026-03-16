import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
from pathlib import Path

# Agregar src a path para imports
sys.path.append(str(Path(__file__).parent.parent.parent))
from app.utils.data_loader import load_all_data, format_number

# Página: Overview (Configurada vía main.py)
st.title("📊 Peru GitHub Ecosystem Overview")

# Cargar Datos
with st.spinner('Cargando datos del dataset...'):
    users_df, repos_df, classifications_df, user_metrics_df, eco_metrics = load_all_data()

if user_metrics_df.empty or not eco_metrics:
    st.warning("⚠️ No se encontraron datos procésados. Por favor ejecute la minería y procesamiento primero.")
    st.stop()

st.markdown("""
Bienvenido al dashboard interactivo del análisis de desarrolladores Peruanos.
Esta plataforma mapea el impacto técnico y económico del software desarrollado en el país.
""")

# Top metrics
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

# 1. Geographic Distribution (MAP)
st.subheader("📍 Geographic Talent Distribution")
geo_data = eco_metrics.get("geo_distribution", {})

if geo_data:
    # Mapeo de coordenadas aproximadas para ciudades peruanas
    city_coords = {
        "Lima": [-12.0464, -77.0428],
        "Arequipa": [-16.4090, -71.5375],
        "Cusco": [-13.5319, -71.9675],
        "Other Peru": [-9.19, -75.01] # Centro del país aproximado
    }
    
    map_list = []
    for city, count in geo_data.items():
        coords = city_coords.get(city, city_coords["Other Peru"])
        map_list.append({
            "City": city,
            "Count": count,
            "lat": coords[0],
            "lon": coords[1]
        })
    
    df_map = pd.DataFrame(map_list)
    
    fig_map = px.scatter_geo(
        df_map,
        lat="lat",
        lon="lon",
        size="Count",
        hover_name="City",
        projection="mercator",
        title="Developer Concentration in Peru",
        template="plotly_dark",
        scope="south america"
    )
    fig_map.update_geos(
        fitbounds="locations",
        visible=True,
        resolution=50,
        showcountries=True,
        countrycolor="RebeccaPurple"
    )
    st.plotly_chart(fig_map, use_container_width=True)

st.divider()

# 2. Key Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top Languages by Byte Volume")
    top_langs = eco_metrics.get("top_languages_by_bytes", {})
    if top_langs:
        langs_df = pd.DataFrame(list(top_langs.items()), columns=['Language', 'Bytes'])
        langs_df['MBs'] = langs_df['Bytes'] / (1024 * 1024)
        langs_df = langs_df[langs_df['Language'] != 'null'].sort_values(by='MBs', ascending=False)
        
        fig_lang = px.bar(
            langs_df.head(10), 
            x='MBs', 
            y='Language',
            orientation='h',
            color='MBs',
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig_lang, use_container_width=True)

with col2:
    st.subheader("Industry Penetration (Top 10)")
    top_inds = eco_metrics.get("top_industries_by_repo_count", {})
    if top_inds:
        inds_df = pd.DataFrame(list(top_inds.items()), columns=['Industry', 'Repo Count'])
        inds_clean = inds_df[inds_df['Industry'] != 'Desconocido'].head(10)
        
        # Truncar nombres de industria largos para mejor visualización
        inds_clean['ShortIndustry'] = inds_clean['Industry'].apply(lambda x: x[:30] + '...' if len(x) > 30 else x)
        
        fig_ind = px.bar(
            inds_clean,
            x='Repo Count',
            y='ShortIndustry',
            orientation='h',
            color='Repo Count',
            color_continuous_scale="Blues"
        )
        st.plotly_chart(fig_ind, use_container_width=True)

st.markdown("---")
st.caption("Data source: GitHub REST API & GPT-4 Industry Classification.")

