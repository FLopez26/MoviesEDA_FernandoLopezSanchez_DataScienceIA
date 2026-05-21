# 🎬 TMDB Movie Analytics — EDA Empresarial

**Máster en Data Science & AI · Proyecto Entregable**

---

## Objetivo

Analizar qué tipos de películas son más rentables en función de su género, presupuesto, valoración y época, con el fin de orientar decisiones de inversión en la industria cinematográfica.

---

## Dataset

| Campo | Detalle |
|-------|---------|
| Fuente | [TMDB Movie Data — Kaggle](https://www.kaggle.com/datasets/kakarlaramcharan/tmdb-data-0920) |
| Archivo | `data/raw/movie_data_tmbd.csv` |
| Separador | `\|` (pipe) |
| Filas brutas | ~120 000 películas |
| Columnas | 27 (título, presupuesto, recaudación, géneros, valoración, fecha…) |

> El CSV completo no está incluido en el repositorio por su tamaño (~400MB). Descárgalo del enlace anterior y colócalo en `data/raw/movie_data_tmbd.csv`.
> Para una ejecución rápida sin el CSV completo, el repositorio incluye `data/raw/sample_movie_data.csv`, una muestra representativa de 2000 películas estratificada por año. Activa `DEMO = True` en el notebook para usarla.

---

## Preguntas de negocio

| ID | Pregunta | Visualización |
|----|----------|---------------|
| **Q1** | ¿Qué géneros tienen mayor ROI y beneficio absoluto históricamente? | Barras horizontales |
| **Q2** | ¿Cómo ha evolucionado la cuota de producción de cada género por décadas? | Mapa de calor |
| **Q3** | ¿Más presupuesto garantiza más recaudación? ¿Varía por género? | Scatter log-log |
| **Q4** | ¿Las películas mejor valoradas son también las más rentables? | Scatter + tendencia |
| **Q5** | ¿Qué géneros están en auge y podrían dominar la próxima década? | Líneas temporales |
| **Q6** | ¿Qué combinación género × rating tier maximiza el ROI? | Mapa de calor |
| **Q7** | ¿Cómo se distribuye el beneficio absoluto por género? | Boxplot |

---

## Estructura del proyecto

```
project_demo/
├── data/
│   ├── raw/
│   │   ├── movie_data_tmbd.csv        ← Dataset completo (no incluido, ver enlace)
│   │   └── sample_movie_data.csv      ← Muestra de 2000 películas para demo
│   └── processed/
│       └── clean_dataset.csv          ← Output del pipeline (en .gitignore)
├── figures/
│   ├── Q1_roi_by_genre.png
│   ├── Q2_genre_decade_heatmap.png
│   ├── Q3_budget_vs_revenue.png
│   ├── Q4_rating_vs_roi.png
│   ├── Q5_genre_trends.png
│   ├── Q6_genre_rating_roi.png
│   └── Q7_profit_boxplot.png
├── notebooks/
│   └── eda.ipynb                      ← Análisis principal (ejecutable de inicio a fin)
├── src/
│   ├── __init__.py
│   ├── config.py                      ← Rutas y constantes
│   ├── io.py                          ← load_csv, export_csv, parse_genre_list
│   ├── cleaning.py                    ← Pipeline de limpieza (clean)
│   ├── features.py                    ← build_features (roi, profit_M, rating_tier)
│   ├── viz.py                         ← 7 funciones de visualización
│   └── utils.py                       ← Validaciones, helpers y tablas resumen
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
cd project_demo

# 2. Crear entorno virtual
python -m venv .venv
source .venv/bin/activate          # macOS/Linux
# .venv\Scripts\activate           # Windows PowerShell

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Añadir el CSV completo en data/raw/movie_data_tmbd.csv
#    (o usar DEMO = True en el notebook con la muestra incluida)

# 5. Ejecutar el pipeline completo
python main.py

# 6. (Opcional) Abrir el notebook
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

### Impacto de los filtros de limpieza

| Etapa | Filas restantes | Filas eliminadas |
|-------|----------------|-----------------|
| Dataset crudo | ~119 938 | — |
| Tras eliminar duplicados | ~119 087 | ~851 |
| Tras filtrar status=Released | ~86 000 | ~33 000 |
| Tras filtrar vote_count ≥ 20 | ~29 812 | ~56 000 |

---

## Features construidas

| Feature | Definición | Registros válidos |
|---------|-----------|-------------------|
| `roi` | (revenue − budget) / budget | 6 361 películas con datos financieros |
| `profit_M` | (revenue − budget) / 1 000 000 | 6 361 películas |
| `rating_tier` | Cuartiles de vote_average: Bajo / Medio / Bueno / Excelente | 29 812 |

---

## Hallazgos principales

### 1. Horror y Animation lideran el ROI mediano *(Q1, Q6, Q7)*
Horror alcanza un ROI mediano del **~145%** y Animation del **~164%**, muy por encima de
los blockbusters de Action (~103%). Animation destaca además por la consistencia de sus
resultados (baja dispersión en Q7), mientras que Horror ofrece mayor potencial pero también
más riesgo. Géneros como Action o Adventure, con ROI más moderado, generan beneficios
absolutos en M$ mayores por el volumen de sus producciones.

### 2. Calidad crítica ≠ rentabilidad *(Q4, Q6)*
La correlación entre valoración TMDB y ROI es prácticamente nula (**r ≈ 0.008**).
Apostar por películas "de calidad" no garantiza beneficio económico. Sin embargo, el cruce
género × rating tier (Q6) matiza esto: en Animation la calidad sí importa, ya que las
películas de tier "Excelente" son las más rentables del género.

### 3. Animation y Horror, los géneros del futuro *(Q1, Q2, Q5, Q7)*
Animation lleva 20 años de crecimiento sostenido en producción manteniendo un ROI
mediano del 164% y beneficios absolutos consistentes. Horror combina bajo coste y
audiencias en expansión. Ambos géneros son la apuesta más sólida para carteras de
inversión 2025–2035.

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
