# 🇵🇪 GitHub Peru Analytics: Developer Ecosystem Dashboard

A comprehensive data analytics platform designed to extract, process, and visualize the Peruvian developer ecosystem. This project combines the GitHub REST API, GPT-4 driven industry classification (CIIU-21), and an interactive Streamlit dashboard with a built-in RAG AI Agent.

---

## 🚀 Easter Egg
Before exploring the data, pay tribute to Python's heritage by running:

```python
import antigravity
```

## 📊 Key Findings
Based on our current dataset of **1,100 repositories** and **19 developers**:

1. **Industry Leadership**: **46.7%** of mapped projects (514 repos) belong to **Industry J (Information & Communication)**, highlighting a robust software development culture.
2. **Education Focus**: **28%** of repositories (308 repos) are classified under **Industry P (Education)**, suggesting high academic participation or EdTech growth.
3. **Geographic Concentration**: **63%** of tracked developers are based in **Lima**, while 37% operate from other regions in Peru.
4. **Community Reach**: High-impact developers average **127.89 followers**, showing a significant reach within the global open-source community.
5. **Technical Diversity**: The ecosystem shows a massive variety of languages, with high-performance languages like C++ and Java being prominent alongside web technologies.

## 🗂️ Data Collection
- **Sources**: GitHub REST API & GraphQL.
- **Search Logic**: Filtered by `location:Peru` and `location:Lima`.
- **Resilience**: Implements `tenacity` for robust error handling and rate-limit compliance.
- **Target**: Reached a milestone of **1,100+ valid repositories**.

## ✨ Features
The platform offers 6 distinct analysis domains:

- **📊 Overview Dashboard**: High-level KPIs, ecosystem totals, and dominant industry trends.
- **🧑‍💻 Developer Explorer**: Profile deep-dives, impact scores, and technical specialization metrics.
- **📦 Repository Browser**: Searchable repo database filtered by stars, language, and industry classification.
- **🏭 Industry Analysis**: Distribution of projects across the 21 CIIU categories and sectoral leaders.
- **💻 Language Analytics**: Dominant technologies measured by codebase volume (Bytes) and repo count.
- **🤖 AI Ecosystem Agent**: A conversational RAG agent that answers complex questions about the Peruvian tech landscape.

## 📁 Repo Structure
├── README.md                    # Main documentation
├── requirements.txt             # Python dependencies
├── .env.example                # Environment template
├── .gitignore                  # Git ignore file
│
├── data/                        # Extracted and processed data
│   ├── raw/                    # Raw API responses
│   ├── processed/              # Cleaned CSVs (1,100+ repos)
│   └── metrics/                # Calculated stats and Agent logs
│
├── src/                         # Source code
│   ├── extraction/             # GitHub API client
│   ├── processing/             # Metric calculation logic
│   └── agents/                 # RAG AI Agent & Classification
│
├── app/                         # Streamlit Dashboard
│   ├── main.py                 # Entry point
│   ├── pages/                  # 6 Interactive pages
│   └── utils/                  # Data loaders and charts
│
├── docs/                        # Project Documentation
│   └── methodology.md          # Technical approach & Rubric details
│
├── scripts/                     # Executable pipeline scripts
└── tests/                       # Unit tests for core logic

## ⚙️ Installation

### Prerequisites
- Python 3.10+
- OpenAI API Key (for classification and AI agent)
- GitHub Personal Access Token (for extraction)

### Steps
1. **Clone the repository**:
   ```bash
   git clone https://github.com/adrianmisi/github-peru-analytics.git
   cd github-peru-analytics
   ```

2. **Setup virtual environment**:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables**:
   Create a `.env` file (see `.env.example`) and add your tokens:
   ```env
   GITHUB_TOKEN=your_github_token
   OPENAI_API_KEY=your_openai_key
   ```

## 🏃 Usage
Follow the pipeline in order to generate and visualize the analytics:

```powershell
# 1. Extract data (GitHub API)
python scripts/extract_data.py

# 2. AI Classification (CIIU-21)
python scripts/classify_repos.py

# 3. Calculate Metrics
python scripts/calculate_metrics.py

# 4. Launch Dashboard
streamlit run app/main.py
```

## ✅ Deliverables Checklist (Rubric Compliance)

- **Extractions**: 1,100+ repositories with full metadata (`data/processed/repositories.csv`).
- **Classification**: GPT-4 Industry classification with confidence and reasoning.
- **Talent Analytics**: Developer clustering (Elite, Expert, Rising) and impact scores.
- **RAG Agent**: AI Assistant with access to ecosystem metrics and interaction logging.
- **Dashboard**: Professional 6-page interface (Overview, Talent, Repos, Industry, Languages, AI Agent).
- **Documentation**: Detailed [Methodology](docs/methodology.md) and [Video Walkthrough](https://drive.google.com/file/d/1O-hH4_Fe_wKA8JuEDrCemDsFrPdK7b_G/view?usp=sharing).
- **Easter Egg**: [Antigravity Screenshot](demo/screenshots/antigravity_screenshot.png)

![Antigravity Proof](demo/screenshots/antigravity_screenshot.png)

## 📐 Metrics Documentation
...


## 🤖 AI Agent Documentation
The project includes a **Retrieval-Augmented Generation (RAG)** agent located in `src/agents/classification_agent.py`.

- **Mechanism**: Loads the latest `ecosystem_metrics.json` as context.
- **Model**: Powered by `gpt-4-turbo`.
- **Interface**: Integrated chat component in the final tab of the Streamlit dashboard.

## ⚠️ Limitations
- **Location Filter**: Developers who do not set their location on GitHub are excluded.
- **Classification Bias**: Generic or placeholder repositories default to Industry J on low-confidence inference.

## 📎 Video
[Interactive Demo & Implementation Walkthrough](https://drive.google.com/file/d/1O-hH4_Fe_wKA8JuEDrCemDsFrPdK7b_G/view?usp=sharing)

## 👤 Author
**Adrian Misi**  
Course: Prompt Engineering  
March 2026
