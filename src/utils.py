"""
utils.py — Funciones reutilizables.
"""
import pandas as pd
from typing import Sequence


def assert_columns(df: pd.DataFrame, required: Sequence[str]) -> None:
    """
    Lanza ValueError si alguna columna no existe en el DataFrame.
    """
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(
            f"[utils] Columnas requeridas no encontradas: {missing}\n"
            f"  Columnas disponibles: {df.columns.tolist()}"
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
