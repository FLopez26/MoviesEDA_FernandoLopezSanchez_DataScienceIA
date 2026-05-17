"""
utils.py — Validaciones y helpers reutilizables.
"""
import pandas as pd
from typing import Sequence


def assert_columns(df: pd.DataFrame, required: Sequence[str]) -> None:
    """
    Lanza ValueError si alguna columna requerida no existe en el DataFrame.
    Útil como guardia al inicio de cada función de transformación.
    """
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"[utils] Columnas requeridas no encontradas: {missing}\n"
            f"  Columnas disponibles: {df.columns.tolist()}"
        )


def assert_no_duplicates(df: pd.DataFrame, subset: str = "id") -> None:
    """Lanza AssertionError si hay duplicados en la columna indicada."""
    n_dup = df.duplicated(subset=subset).sum()
    assert n_dup == 0, f"[utils] {n_dup:,} duplicados encontrados en '{subset}'"


def assert_positive(df: pd.DataFrame, col: str) -> None:
    """Verifica que todos los valores no-nulos de una columna sean > 0."""
    invalid = (df[col].dropna() <= 0).sum()
    assert invalid == 0, (
        f"[utils] {invalid:,} valores no positivos en '{col}'"
    )


def explode_genres(df: pd.DataFrame) -> pd.DataFrame:
    """
    Expande el DataFrame para que cada fila represente una película-género.
    Útil para análisis de distribución de géneros.
    Requiere que 'genre_list' ya exista (creada en cleaning.expand_genres).
    """
    assert_columns(df, ["genre_list"])
    df_exp = df.explode("genre_list").rename(columns={"genre_list": "genre"})
    df_exp = df_exp[df_exp["genre"].notna() & (df_exp["genre"] != "")]
    return df_exp.reset_index(drop=True)


def decade_label(year: int) -> str:
    """Devuelve la etiqueta de década para un año dado. Ej: 1995 → '1990s'."""
    return f"{(year // 10) * 10}s"


def summary_stats(df: pd.DataFrame, col: str) -> dict:
    """Estadísticos básicos de una columna numérica como dict."""
    s = df[col].dropna()
    return {
        "count": int(s.count()),
        "mean":  round(float(s.mean()), 4),
        "median":round(float(s.median()), 4),
        "std":   round(float(s.std()), 4),
        "min":   round(float(s.min()), 4),
        "max":   round(float(s.max()), 4),
    }
