# Methodology: GitHub Peru Analytics

This document outlines the technical approach, data pipeline, and AI integration for the **GitHub Peru Analytics** project.

## 1. Data Extraction & Mining
The extraction process targets developers located in Peru to map the national tech ecosystem.

- **Source**: GitHub REST API (v3).
- **Scope**: 1,100+ repositories.
- **Criteria**: Users with `location:Peru` or `location:Lima`.
- **Metrics Extracted**:
    - **Repository Level**: Stars, forks, primary languages (bytes), description, and README content.
    - **User Level**: Followers, public repository count, and technical activity (Total Issues and PRs opened).
- **Resilience**: Implements exponential backoff and rate-limit handling via the `tenacity` library.

## 2. AI-Powered Industry Classification
To understand the economic impact, each repository is classified into one of the **21 CIIU (Rev. 4)** industrial categories.

- **Model**: GPT-4o-mini / GPT-4 Turbo.
- **Input**: Repository name, description, and the first 5,000 characters of the `README.md`.
- **Output**: 
    - **CIIU Code**: (e.g., J for Information & Communication, K for Finance).
    - **Confidence Score**: (0.0 to 1.0).
    - **Reasoning**: A detailed explanation of why the AI chose that specific sector.
- **Fallback**: Repositories with vague metadata default to Industry J (Information & Communication) with lower confidence.

## 3. Talent Analytics & Clustering
The project goes beyond raw counts by "clustering" developers based on their technical footprint.

- **Influence Score**: `Stars + Followers`.
- **Activity Score**: Total Non-forked repositories.
- **Engagement**: Total Forks received.
- **Clustering Logic**:
    - **Elite**: Influence > 500.
    - **Expert**: Influence > 100 or Activity > 50.
    - **Polyglot**: Technical score (Unique Languages) > 5.
    - **Rising Talent**: Base category for new high-quality contributors.

## 4. RAG AI Agent (Retrieval-Augmented Generation)
The dashboard features an AI analyst that can answer complex questions about the dataset.

- **Architecture**: Retrieval-Augmented Generation (RAG).
- **Context**: The agent injects the `ecosystem_metrics.json` (global stats, geographic distribution, language trends) into the system prompt.
- **Transparency**: Every interaction is logged in `data/metrics/agent_run_log.json`, including the question, context summary, and the AI's response.

## 5. Visualizations
Visual insights are provided via **Streamlit** and **Plotly**:
- **Geographic Mapping**: Coordinate-based talent density map of Peru.
- **Industry Funnels**: Sectoral distribution and penetration.
- **Language Heatmaps**: Tech stack volume per industrial sector.
- **Talent Scatters**: Visualizing the "Developer Landscape" (Impact vs Activity).
