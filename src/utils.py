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

def quality_check_filters(df_raw: pd.DataFrame) -> None:
    """
    Muestra el impacto de cada filtro de limpieza sobre el dataset crudo:
    duplicados, status, vote_count y año de lanzamiento.
    """
    n_raw = len(df_raw)
    print(f"{'Etapa':<40} {'Filas':>8}  {'Eliminadas':>10}  {'% perdido':>9}")
    print("-" * 72)
    print(f"{'Dataset crudo':<40} {n_raw:>8,}")

    df_tmp = df_raw.copy()
    df_tmp["id_num"] = pd.to_numeric(df_tmp["id"], errors="coerce")
    n_after_dedup = n_raw - df_tmp.duplicated(subset="id_num", keep="first").sum()
    n_dup = n_raw - n_after_dedup
    print(f"{'Tras eliminar duplicados (id)':<40} {n_after_dedup:>8,}  {n_dup:>10,}  {n_dup/n_raw*100:>8.1f}%")

    n_released = (df_raw["status"] == "Released").sum()
    n_not_released = n_raw - n_released
    print(f"{'Tras filtrar status=Released':<40} {n_released:>8,}  {n_not_released:>10,}  {n_not_released/n_raw*100:>8.1f}%")

    vote_num = pd.to_numeric(df_raw["vote_count"], errors="coerce")
    n_votes = ((df_raw["status"] == "Released") & (vote_num >= 20)).sum()
    n_lost_votes = n_released - n_votes
    print(f"{'Tras filtrar vote_count >= 20':<40} {n_votes:>8,}  {n_lost_votes:>10,}  {n_lost_votes/n_raw*100:>8.1f}%")

    year = pd.to_datetime(df_raw["release_date"], errors="coerce").dt.year
    n_year = ((df_raw["status"] == "Released") & (vote_num >= 20) & (year >= 1900)).sum()
    n_lost_year = n_votes - n_year
    print(f"{'Tras filtrar release_year >= 1900':<40} {n_year:>8,}  {n_lost_year:>10,}  {n_lost_year/n_raw*100:>8.1f}%")
    print("-" * 72)
    print(f"{'Dataset final (limpio)':<40} {n_year:>8,}  {n_raw - n_year:>10,}  {(n_raw-n_year)/n_raw*100:>8.1f}%")


def quality_check_financial(df: pd.DataFrame, top_genres: list) -> None:
    """
    Muestra la cobertura financiera por género:
    número de películas con ROI calculable, ROI mediano y beneficio mediano.
    """
    from IPython.display import display
    df_exp = explode_genres(df[df["roi"].notna()])
    cobertura = (
        df_exp[df_exp["genre"].isin(top_genres)]
        .groupby("genre")
        .agg(
            n_con_roi       = ("roi",      "count"),
            roi_mediano     = ("roi",      lambda x: f"{x.median()*100:.0f}%"),
            profit_mediano_M= ("profit_M", lambda x: f"{x.median():.1f}M$"),
        )
        .sort_values("n_con_roi", ascending=False)
    )
    print("Resumen financiero por género (solo películas con datos completos):")
    display(cobertura)

def tabla_roi_por_genero(df: pd.DataFrame, top_genres: list) -> None:
    """Tabla resumen: Género × ROI mediano y beneficio absoluto."""
    from IPython.display import display
    df_exp = explode_genres(df[df["roi"].notna()])
    tabla = (
        df_exp[df_exp["genre"].isin(top_genres)]
        .groupby("genre")
        .agg(
            n_peliculas    = ("roi",      "count"),
            roi_mediano    = ("roi",      "median"),
            profit_mediano = ("profit_M", "median"),
            profit_medio   = ("profit_M", "mean"),
        )
        .assign(roi_pct=lambda x: (x["roi_mediano"] * 100).round(1).astype(str) + "%")
        .sort_values("roi_mediano", ascending=False)
        [["n_peliculas", "roi_pct", "profit_mediano", "profit_medio"]]
        .rename(columns={
            "n_peliculas":    "N películas",
            "roi_pct":        "ROI mediano",
            "profit_mediano": "Beneficio mediano (M$)",
            "profit_medio":   "Beneficio medio (M$)",
        })
    )
    print("Género × ROI mediano y beneficio absoluto:")
    display(tabla.round(2))


def tabla_decada_por_genero(df: pd.DataFrame, top_genres: list) -> None:
    """Tabla resumen: Década × Cuota de producción (%)."""
    from IPython.display import display
    df_exp = explode_genres(df[df["decade"].notna()])
    df_exp = df_exp[
        df_exp["genre"].isin(top_genres) &
        df_exp["decade"].isin([f"{d}s" for d in range(1960, 2020, 10)])
    ]
    pivot = (
        df_exp.groupby(["decade", "genre"])
        .size()
        .unstack(fill_value=0)
    )
    pivot_pct = (pivot.div(pivot.sum(axis=1), axis=0) * 100).round(1)
    print("Cuota de producción por género y década (%):")
    display(pivot_pct)


def tabla_rating_tier(df: pd.DataFrame) -> None:
    """Tabla resumen: Rating Tier × ROI mediano y beneficio absoluto."""
    from IPython.display import display
    tabla = (
        df[df["roi"].notna()]
        .groupby("rating_tier", observed=True)
        .agg(
            n_peliculas    = ("roi",      "count"),
            roi_mediano    = ("roi",      "median"),
            profit_mediano = ("profit_M", "median"),
        )
        .assign(roi_pct=lambda x: (x["roi_mediano"] * 100).round(1).astype(str) + "%")
        [["n_peliculas", "roi_pct", "profit_mediano"]]
        .rename(columns={
            "n_peliculas":    "N películas",
            "roi_pct":        "ROI mediano",
            "profit_mediano": "Beneficio mediano (M$)",
        })
    )
    print("Rating Tier × ROI mediano y beneficio absoluto:")
    display(tabla.round(2))


def tabla_genero_rating_pivot(df: pd.DataFrame, top_genres: list) -> None:
    """Tabla resumen: Género × Rating Tier (pivot de ROI mediano %)."""
    from IPython.display import display
    df_exp = explode_genres(df[df["roi"].notna() & df["rating_tier"].notna()])
    df_exp = df_exp[df_exp["genre"].isin(top_genres)]
    pivot = (
        df_exp.groupby(["genre", "rating_tier"], observed=True)["roi"]
        .median()
        .unstack()
        * 100
    ).round(1)
    print("ROI mediano (%) por Género × Rating Tier:")
    display(pivot)