# 🎬 TMDB Movie Analytics — EDA Empresarial

**Máster en Data Science & AI · Proyecto Entregable**

---

## Objetivo

Responder 5 preguntas estratégicas de negocio sobre la industria cinematográfica global
usando datos reales de TMDB (~120 000 películas). El análisis está orientado a **apoyar
decisiones de inversión y producción** con evidencia cuantitativa.

---

## Dataset

| Campo | Detalle |
|-------|---------|
| Fuente | [TMDB Movie Data — Kaggle](https://www.kaggle.com/datasets/kakarlaramcharan/tmdb-data-0920) |
| Archivo | `data/raw/movie_data_tmbd.csv` |
| Separador | `\|` (pipe) |
| Filas brutas | ~120 000 películas |
| Columnas | 27 (título, presupuesto, recaudación, géneros, valoración, fecha…) |

---

## Preguntas de negocio

| ID | Pregunta | Visualización |
|----|----------|---------------|
| **Q1** | ¿Qué géneros tienen mayor ROI (Retorno sobre la Inversión) históricamente? | Barras horizontales |
| **Q2** | ¿Cómo ha evolucionado la cuota de producción de cada género por décadas? | Mapa de calor |
| **Q3** | ¿Más presupuesto garantiza más recaudación? ¿Varía por género? | Scatter log-log |
| **Q4** | ¿Las películas mejor valoradas son también las más rentables? | Scatter + tendencia |
| **Q5** | ¿Qué géneros están en auge y podrían dominar la próxima década? | Líneas temporales |

---

## Estructura del proyecto

```
MoviesEDA_FernandoLopezSanchez_DataScienceIA/
├── data/
│   ├── raw/
│   │   └── movie_data_tmbd.csv        ← Dataset original (Debido al tamaño del .csv se debe añadir manualmente ya que se encuentra en gitignore)
│   └── processed/
│       └── clean_dataset.csv          ← Output del pipeline (Se creará al final de las ejecuciones de código)
├── figures/
│   ├── Q1_roi_by_genre.png
│   ├── Q2_genre_decade_heatmap.png
│   ├── Q3_budget_vs_revenue.png
│   ├── Q4_rating_vs_roi.png
│   └── Q5_genre_trends.png
├── notebooks/
│   └── eda.ipynb                      ← Análisis principal (ejecutable de inicio a fin)
├── src/
│   ├── __init__.py
│   ├── config.py                      ← Rutas y constantes
│   ├── io.py                          ← load_csv, export_csv, parse_genre_list
│   ├── cleaning.py                    ← Pipeline de limpieza (clean)
│   ├── features.py                    ← build_features (roi, profit_M, rating_tier)
│   ├── viz.py                         ← 5 funciones de visualización
│   └── utils.py                       ← Validaciones y helpers
├── main.py                            ← Entrypoint reproducible
├── requirements.txt
└── README.md
```

---

## Pipeline reproducible

```
load_csv() → clean() → build_features() → export_csv() → plot_all()
```

### Pasos para ejecutar

```bash
# 1. Entrar en la carpeta
cd MoviesEDA_FernandoLopezSanchez_DataScienceIA

# 2. Crear entorno virtual (opcional pero recomendado)
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\Scripts\activate           # Windows PowerShell

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar el pipeline completo
python main.py

# 5. (Opcional) Abrir el notebook
jupyter notebook notebooks/eda.ipynb
```

---

## Transformaciones clave

| Problema | Solución |
|----------|----------|
| Columna `genres` como string JSON-like | `ast.literal_eval` → lista de nombres |
| `release_date` como texto | `pd.to_datetime` + extracción de año y década |
| Todos los tipos en `str` (carga defensiva) | `pd.to_numeric(errors='coerce')` |
| 851 duplicados por ID TMDB | `drop_duplicates(subset='id')` |
| Películas sin estrenar o sin votos | Filtro `status=Released` y `vote_count ≥ 20` |

---

## Features construidas

| Feature | Definición | Registros válidos |
|---------|-----------|-------------------|
| `roi` | (revenue − budget) / budget | 6 361 películas con datos financieros |
| `profit_M` | (revenue − budget) / 1 000 000 | Ídem |
| `rating_tier` | Cuartiles de vote_average: Bajo / Medio / Bueno / Excelente | 29 812 |

---

## Hallazgos principales

### 1. Horror y Animation lideran el ROI mediano *(Q1)*
Horror alcanza un ROI mediano del **~201%** y Animation del **~145%**, muy por encima de
los blockbusters de Action (~99%). Con presupuestos relativamente bajos, estos géneros
ofrecen el mejor retorno por euro invertido.

### 2. Calidad crítica ≠ rentabilidad *(Q4)*
La correlación entre valoración TMDB y ROI es prácticamente nula (**r ≈ 0.008**).
Apostar por películas "de calidad" no garantiza beneficio económico.

### 3. Animation y Horror, los géneros del futuro *(Q1 + Q5)*
Animation lleva 20 años de crecimiento sostenido en producción manteniendo alto ROI.
Horror combina bajo coste y audiencias en expansión. Ambos géneros son la apuesta
más sólida para carteras de inversión 2025–2035.

---

## Posibles siguientes pasos

- Incorporar datos de plataformas streaming (Netflix, Disney+)
- Análisis de impacto de director/elenco en ROI
- Modelo predictivo de ROI con XGBoost o regresión regularizada
- Dashboard interactivo con Streamlit o Plotly Dash

---

## Requisitos

```
pandas>=2.0
numpy>=1.24
matplotlib>=3.7
seaborn>=0.12
jupyter
nbformat
```

Ver `requirements.txt` para versiones exactas.
