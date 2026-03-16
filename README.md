# GitHub Peru Analytics 🇵🇪

Plataforma integral orientada a la extracción, clasificación y análisis de métricas sobre de la comunidad de desarrolladores de software en el Perú a través de la API oficial de GitHub y la inferencia de Inteligencia Artificial.

## 1. Project Context
Este proyecto nace como respuesta a la necesidad de comprender el ecosistema tecnológico peruano. Al procesar más de 1,000 repositorios de código abierto impulsados por programadores del país, buscamos identificar quiénes son los principales influyentes, qué tecnologías lideran el mercado nacional, y en qué sectores empresariales o industriales (Clasificación CIIU) el software tiene un impacto más fuerte dentro en Perú.

## 2. Methodology and Tools

### Metodología de Muestreo y Extracción
- Se utilizó la Github GraphQL & REST API para consultar usuarios localizados bajo el search param `location:Peru` y `location:Lima` hasta conseguir un mínimo superior a los 1,000 repositorios válidos.
- Extracción de metadata granular: Fechas, descripciones, y **contenido clave del README** por cada proyecto. Se aplicó rate-limiting resiliente mediante la librería `Tenacity`.

### Inteligencia Artificial (AI Integration)
- **Sector Classification**: El contenido del README y descripción de cada uno de los 1,000+ repositorios extraídos fue ingerido asíncronamente por el LLM **GPT-4-Turbo de OpenAI**, al cual se le instruyó a predecir a qué categoría de la tabla **CIIU 21** corresponde el código (Industria, Salud, Fintech, etc).
- **Interactive AI Agent**: Agente de Retrieval interactivo alimentado por el conteo maestro de la extracción de datos, lo que permite consultas por chat sobre los insights minados en la plataforma con el mismo modelo GPT-4.

### Technologies
- **Python**: Core para los requests, parseo JSON, scripts asíncronos y NLP.
- **OpenAI API**: Base fundamental de inferencia determinística en JSON de categorías industriales y del Chatbot Analítico.
- **Streamlit**: Despliegue de la interfaz web con interactividad (Dashboards y filtros cross-component).
- **Plotly Express / Pandas**: Para el modelado y visualización de la data.

## 3. Results and Insights
*(Ver en detalle corriendo el Dashboard de Streamlit)*
- Se logró catalogar holgadamente y con éxito la cuota de **1100 Repositorios y 19 Desarrolladores Peruanos influyentes**.
- **Software Educativo (P - Enseñanza) e IT (J - Información y Comunicación)** muestran una penetración abismal sobre otro tipo de corporativos en el desarrollo peruano, esto es un indicador de la alta participación técnica de estudiantes o profesores universitarios y servicios de software puro de Lima hacia el mundo.
- Se ha notado la tendencia a usar lenguajes como C++, Java o TS a gran escala.

## 4. Setup Instructions

Para correr el proyecto localmente (Windows):

1. **Clonar Repo e ingresar**:
```bash
git clone https://github.com/Tu-Usuario/github-peru-analytics.git
cd github-peru-analytics
```

2. **Crear y activar Virtual Environment**:
```bash
python -m venv venv
.\venv\Scripts\activate
```

3. **Instalar Dependencias**:
```bash
pip install -r requirements.txt
```

4. **Configurar Credenciales (.env)**:
Renombrar o copiar el `.env.example` a `.env` y rellenar con tus tokens:
```
GITHUB_TOKEN=tu_token_de_github
OPENAI_API_KEY=tu_token_de_openai
```

## Project Structure

La organización de archivos del proyecto sigue el siguiente esquema:

```text
github-peru-analytics/
│
├── README.md                    # Documentación principal
├── requirements.txt             # Dependencias de Python
├── .env.example                # Plantilla de entorno
├── .gitignore                  # Archivo de exclusión de Git
│
├── data/                        # Datos extraídos y procesados
│   ├── raw/                    # Respuestas crudas de API
│   │   ├── users/
│   │   └── repos/
│   ├── processed/              # Datos limpios y finales
│   │   ├── users.csv
│   │   ├── repositories.csv
│   │   └── classifications.csv
│   └── metrics/                # Métricas calculadas
│       ├── user_metrics.csv
│       └── ecosystem_metrics.json
│
├── src/                         # Código fuente
│   ├── __init__.py
│   ├── extraction/             # Extracción de la API de GitHub
│   │   ├── __init__.py
│   │   ├── github_client.py
│   │   ├── user_extractor.py
│   │   └── repo_extractor.py
│   ├── database/               # Almacenamiento de datos (placeholders)
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── crud.py
│   ├── classification/         # Clasificación industrial
│   │   ├── __init__.py
│   │   └── industry_classifier.py
│   ├── metrics/                # Cálculo de métricas
│   │   ├── __init__.py
│   │   ├── user_metrics.py
│   │   └── ecosystem_metrics.py
│   └── agents/                 # Agentes de IA
│       ├── __init__.py
│       └── classification_agent.py
│
├── app/                         # Aplicación Dashboard (Streamlit)
│   ├── main.py                 # Punto de entrada principal
│   ├── pages/
│   │   ├── 1_Overview.py
│   │   ├── 2_Developers.py
│   │   ├── 3_Repositories.py
│   │   ├── 4_Industries.py
│   │   └── 5_Languages.py
│   └── components/
│       └── charts.py
│
├── scripts/                     # Scripts de ejecución
│   ├── extract_data.py         # Ejecutar extracción
│   ├── classify_repos.py       # Ejecutar clasificación
│   └── calculate_metrics.py    # Calcular todas las métricas
│
├── notebooks/                   # Jupyter notebooks (exploración)
│   └── exploration.ipynb
│
├── demo/                        # Materiales de demostración
│   ├── screenshots/
│   │   ├── overview.png
│   │   ├── developers.png
│   │   └── industries.png
│   ├── video_link.md
│   └── antigravity_screenshot.png  # Captura de pantalla del easter egg
│
└── tests/                       # Pruebas unitarias
    ├── test_extraction.py
    ├── test_classification.py
    └── test_metrics.py
```

## 5. Usage

Para regenerar los datos o ver los resultados:

1. **Extracción**: `python scripts/extract_data.py`
2. **Clasificación**: `python scripts/classify_repos.py`
3. **Métricas**: `python scripts/calculate_metrics.py`
4. **Dashboard**: `streamlit run app/main.py`

## 7. About AI Agents Integration
El proyecto contiene la carpeta `src/agents`. Dentro se encuentra `classification_agent.py`.
Este Agente embebe el conocimiento del procesamiento total del dataset en el backend...

