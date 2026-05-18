"""
io.py — Carga y exportación de datos.
"""
import ast
import pandas as pd
from pathlib import Path
from src.config import RAW_PATH, OUT_PATH


def load_csv(path: Path = RAW_PATH) -> pd.DataFrame:
    """
    Carga el CSV de TMDB (separador '|')
    las líneas mal formadas que contienen overviews multilínea.
    Devuelve un DataFrame con todas las columnas en crudo.
    """
    df = pd.read_csv(
        path,
        sep="|",
        on_bad_lines="skip",
        engine="python",
        dtype=str,               # carga todo como str para manejar nulls

    )
    return df


def export_csv(df: pd.DataFrame, path: Path = OUT_PATH) -> None:
    """Guarda el DataFrame limpio en data/processed/."""
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"[io] Dataset exportado → {path}  ({len(df):,} filas)")


def parse_genre_list(genre_str: str) -> list[str]:
    """
    Convierte la columna 'genres' de formato JSON-like a lista de nombres.
    Ejemplo: "[{'id': 28, 'name': 'Action'}]" → ['Action']
    Devuelve [] si el campo está vacío o es inválido.
    """
    if pd.isna(genre_str) or genre_str in ("", "[]", "nan"):
        return []
    try:
        parsed = ast.literal_eval(genre_str)
        return [g["name"] for g in parsed if isinstance(g, dict) and "name" in g]
    except (ValueError, SyntaxError):
        return []
