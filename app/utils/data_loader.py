import pandas as pd
import json
from pathlib import Path
import streamlit as st

@st.cache_data
def load_all_data():
    base_dir = Path(__file__).parent.parent.parent
    processed_dir = base_dir / "data" / "processed"
    metrics_dir = base_dir / "data" / "metrics"
    
    # Intentar cargar CSVs
    users_df = pd.DataFrame()
    repos_df = pd.DataFrame()
    classifications_df = pd.DataFrame()
    user_metrics_df = pd.DataFrame()
    eco_metrics = {}
    
    # Ahora ambos están en processed
    if (processed_dir / "users.csv").exists():
        users_df = pd.read_csv(processed_dir / "users.csv")
        
    if (processed_dir / "repositories.csv").exists():
        repos_df = pd.read_csv(processed_dir / "repositories.csv")
        
    if (processed_dir / "classifications.csv").exists():
        classifications_df = pd.read_csv(processed_dir / "classifications.csv")
        
    if (metrics_dir / "user_metrics.csv").exists():
        user_metrics_df = pd.read_csv(metrics_dir / "user_metrics.csv")
        
    if (metrics_dir / "ecosystem_metrics.json").exists():
        with open(metrics_dir / "ecosystem_metrics.json", "r", encoding="utf-8") as f:
            eco_metrics = json.load(f)
            
    return users_df, repos_df, classifications_df, user_metrics_df, eco_metrics


def format_number(num):
    if pd.isna(num):
        return "0"
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    if num >= 1_000:
        return f"{num/1_000:.1f}K"
    return f"{int(num)}"
