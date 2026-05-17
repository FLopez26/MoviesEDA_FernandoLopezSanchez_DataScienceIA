"""
features.py — Ingeniería de features para análisis de negocio cinematográfico.
"""
import numpy as np
import pandas as pd
from src.config import MIN_BUDGET, MIN_REVENUE


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Construye 3 features derivadas con valor analítico para el negocio:

    Feature 1 — roi (Return On Investment)
        ROI = (revenue - budget) / budget
        Solo para películas con budget y revenue suficientes.
        El resto se marca como NaN (no aplica).

    Feature 2 — profit_M (Beneficio absoluto en millones USD)
        profit_M = (revenue - budget) / 1_000_000
        Permite comparar magnitudes sin escala logarítmica.

    Feature 3 — rating_tier (Segmentación de calidad)
        Agrupa vote_average en cuartiles con etiquetas de negocio:
        'Bajo' (<5.5) | 'Medio' (5.5-6.5) | 'Bueno' (6.5-7.5) | 'Excelente' (>=7.5)
        Condicional a vote_count >= umbral mínimo (ya filtrado en cleaning).
    """
    df = df.copy()

    # ── Feature 1: ROI ───────────────────────────────────────────────────────
    mask_roi = (df["budget"] >= MIN_BUDGET) & (df["revenue"] >= MIN_REVENUE)
    df["roi"] = np.nan
    df.loc[mask_roi, "roi"] = (
        (df.loc[mask_roi, "revenue"] - df.loc[mask_roi, "budget"])
        / df.loc[mask_roi, "budget"]
    )

    # ── Feature 2: Beneficio absoluto (M$) ──────────────────────────────────
    df["profit_M"] = np.nan
    df.loc[mask_roi, "profit_M"] = (
        df.loc[mask_roi, "revenue"] - df.loc[mask_roi, "budget"]
    ) / 1_000_000

    # ── Feature 3: Tier de calidad ───────────────────────────────────────────
    bins   = [0, 5.5, 6.5, 7.5, 10.1]
    labels = ["Bajo", "Medio", "Bueno", "Excelente"]
    df["rating_tier"] = pd.cut(
        df["vote_average"],
        bins=bins,
        labels=labels,
        right=False,
        include_lowest=True,
    )

    n_roi = mask_roi.sum()
    print(f"[features] ROI calculado para {n_roi:,} películas con datos financieros completos")
    print(f"[features] Rating tiers: {df['rating_tier'].value_counts().to_dict()}")
    return df
