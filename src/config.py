"""
config.py — Rutas y constantes globales del proyecto.
"""
from pathlib import Path

# Raíz del proyecto
ROOT = Path(__file__).resolve().parent.parent

# Paths
RAW_PATH  = ROOT / "data" / "raw"  / "movie_data_tmbd.csv"
OUT_PATH  = ROOT / "data" / "processed" / "clean_dataset.csv"
FIG_PATH  = ROOT / "figures"

# Constantes
MIN_BUDGET  = 10_000        # presupuesto mínimo para considerar una película
MIN_REVENUE = 10_000        # recaudación mínima para calcular ROI
MIN_VOTES   = 20            # votos mínimos para que la valoración sea fiable

# Géneros principales
TOP_GENRES = [
    "Action", "Adventure", "Animation", "Comedy", "Crime",
    "Documentary", "Drama", "Fantasy", "Horror",
    "Romance", "Science Fiction", "Thriller",
]

# Colores para visualizaciones
PALETTE = {
    "primary":   "#2563EB",
    "secondary": "#7C3AED",
    "accent":    "#F59E0B",
    "danger":    "#DC2626",
    "success":   "#16A34A",
    "neutral":   "#6B7280",
}
