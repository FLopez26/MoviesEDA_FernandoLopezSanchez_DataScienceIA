"""
cleaning.py — Limpieza y transformación.
"""
import pandas as pd
from src.config import MIN_VOTES
from src.io import parse_genre_list
from src.utils import assert_columns


REQUIRED_COLUMNS = [
    "title", "budget", "revenue", "genres",
    "vote_average", "vote_count", "release_date", "runtime",
]


def cast_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Convierte columnas numéricas clave de str a float/int."""
    numeric_cols = {
        "budget":       "float64",
        "revenue":      "float64",
        "popularity":   "float64",
        "runtime":      "float64",
        "vote_average": "float64",
        "vote_count":   "float64",
    }
    for col, dtype in numeric_cols.items():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").astype(dtype)
    return df


def parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    """
    Convierte release_date a datetime.
    Extrae: release_year (int), decade (str, ej. '2010s').
    """
    df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")
    df["release_year"] = df["release_date"].dt.year.astype("Int64")
    df["decade"] = (df["release_year"] // 10 * 10).astype("Int64").astype(str) + "s"
    df.loc[df["release_year"].isna(), "decade"] = pd.NA
    return df


def expand_genres(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parsea la columna 'genres' y almacena:
      - genre_list : lista Python de nombres de género
      - primary_genre : primer género (o NaN)
    """
    df["genre_list"]     = df["genres"].apply(parse_genre_list)
    df["primary_genre"]  = df["genre_list"].apply(
        lambda g: g[0] if g else pd.NA
    )
    return df


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina duplicados exactos por id TMDB (conserva primero)."""
    before = len(df)
    df = df.drop_duplicates(subset="id", keep="first")
    print(f"[cleaning] Duplicados eliminados: {before - len(df):,}")
    return df


def filter_valid(df: pd.DataFrame) -> pd.DataFrame:
    """
    Filtra filas con datos mínimamente útiles:
      - Películas con status 'Released'
      - Año de lanzamiento plausible (>= 1900)
      - vote_count >= MIN_VOTES para análisis de valoraciones
    """
    mask = (
        (df["status"] == "Released") &
        (df["release_year"] >= 1900) &
        (df["vote_count"] >= MIN_VOTES)
    )
    before = len(df)
    df = df[mask].copy()
    print(f"[cleaning] Filtrado válido: {before:,} → {len(df):,} filas")
    return df


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pipeline completo de limpieza:
    1. Valida columnas requeridas
    2. Conversión numérica
    3. Fechas y décadas
    4. Expansión de géneros
    5. Eliminación de duplicados
    6. Filtrado de registros inválidos
    """
    assert_columns(df, REQUIRED_COLUMNS)
    df = cast_numeric(df)
    df = parse_dates(df)
    df = expand_genres(df)
    df = remove_duplicates(df)
    df = filter_valid(df)

    # Normalización de texto: título sin espacios extremos
    df["title"] = df["title"].str.strip()

    print(f"[cleaning] Dataset limpio: {len(df):,} películas listas para análisis")
    return df
