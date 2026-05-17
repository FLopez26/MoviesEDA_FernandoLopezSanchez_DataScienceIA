"""
viz.py — Visualizaciones orientadas a negocio cinematográfico.
Cada función genera y guarda su gráfico, y devuelve la Figure de matplotlib.
"""
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path

from src.config import FIG_PATH, TOP_GENRES, PALETTE
from src.utils import explode_genres

warnings.filterwarnings("ignore")

# ── Estilo base ──────────────────────────────────────────────────────────────
plt.rcParams.update({
    "figure.dpi":      150,
    "font.family":     "sans-serif",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid":       True,
    "grid.alpha":      0.3,
    "grid.linestyle":  "--",
})


def _save(fig: plt.Figure, name: str) -> None:
    FIG_PATH.mkdir(parents=True, exist_ok=True)
    path = FIG_PATH / name
    fig.savefig(path, bbox_inches="tight")
    print(f"[viz] Guardado → {path}")


# ────────────────────────────────────────────────────────────────────────────
# Q1 — ROI mediano por género (barras horizontales)
# ────────────────────────────────────────────────────────────────────────────
def plot_roi_by_genre(df: pd.DataFrame) -> plt.Figure:
    """
    Q1: ¿Qué géneros tienen mayor ROI históricamente?
    Usa la mediana del ROI (resistente a outliers) para cada género.
    Solo incluye películas con datos financieros válidos (roi no-nulo).
    """
    df_roi = df[df["roi"].notna()].copy()
    df_exp = explode_genres(df_roi)
    df_exp = df_exp[df_exp["genre"].isin(TOP_GENRES)]

    stats = (
        df_exp.groupby("genre")["roi"]
        .agg(roi_median="median", count="count")
        .reset_index()
        .query("count >= 30")
        .sort_values("roi_median", ascending=True)
    )

    fig, ax = plt.subplots(figsize=(10, 7))
    colors = [PALETTE["success"] if v >= 0 else PALETTE["danger"] for v in stats["roi_median"]]
    bars = ax.barh(stats["genre"], stats["roi_median"] * 100, color=colors, edgecolor="white", linewidth=0.5)

    # Etiquetas de valor
    for bar, val in zip(bars, stats["roi_median"]):
        ax.text(
            bar.get_width() + 1.5, bar.get_y() + bar.get_height() / 2,
            f"{val*100:.0f}%", va="center", fontsize=9, color="#374151"
        )

    ax.axvline(0, color="#374151", linewidth=1)
    ax.set_xlabel("ROI Mediano (%)", fontsize=11)
    ax.set_title("Q1 · ROI Mediano Histórico por Género\n"
                 "Mediana del retorno sobre inversión (sólo películas con datos financieros)",
                 fontsize=13, fontweight="bold", pad=15)
    ax.set_xlim(left=min(stats["roi_median"].min() * 100 - 10, -20))

    # Nota de recuento
    for i, (_, row) in enumerate(stats.iterrows()):
        ax.text(
            ax.get_xlim()[0] + 2, i, f"n={row['count']}", va="center",
            fontsize=7, color="#6B7280"
        )

    fig.tight_layout()
    _save(fig, "Q1_roi_by_genre.png")
    return fig


# ────────────────────────────────────────────────────────────────────────────
# Q2 — Cuota de producción por género y década (heatmap)
# ────────────────────────────────────────────────────────────────────────────
def plot_genre_decade_heatmap(df: pd.DataFrame) -> plt.Figure:
    """
    Q2: ¿Cómo ha evolucionado la cuota de producción de cada género por décadas?
    Muestra el porcentaje de películas de cada género respecto al total de su década.
    """
    df_exp = explode_genres(df[df["decade"].notna()])
    df_exp = df_exp[df_exp["genre"].isin(TOP_GENRES)]

    # Filtrar décadas completas (1960s-2010s para evitar ruido)
    valid_decades = [f"{d}s" for d in range(1960, 2020, 10)]
    df_exp = df_exp[df_exp["decade"].isin(valid_decades)]

    pivot = (
        df_exp.groupby(["decade", "genre"])
        .size()
        .unstack(fill_value=0)
    )
    # Normalizar por décadas → % de cada género en esa década
    pivot_pct = pivot.div(pivot.sum(axis=1), axis=0) * 100

    fig, ax = plt.subplots(figsize=(13, 7))
    sns.heatmap(
        pivot_pct.T,
        ax=ax,
        cmap="YlOrRd",
        annot=True,
        fmt=".1f",
        linewidths=0.5,
        linecolor="#E5E7EB",
        cbar_kws={"label": "% de producción en la década"},
        annot_kws={"size": 9},
    )
    ax.set_title(
        "Q2 · Cuota de Producción por Género y Década (%)\n"
        "Porcentaje de películas de cada género respecto al total de su década",
        fontsize=13, fontweight="bold", pad=15
    )
    ax.set_xlabel("Década", fontsize=11)
    ax.set_ylabel("Género", fontsize=11)
    ax.tick_params(axis="x", rotation=0)
    ax.tick_params(axis="y", rotation=0)

    fig.tight_layout()
    _save(fig, "Q2_genre_decade_heatmap.png")
    return fig


# ────────────────────────────────────────────────────────────────────────────
# Q3 — Presupuesto vs Recaudación log-log coloreado por género
# ────────────────────────────────────────────────────────────────────────────
def plot_budget_vs_revenue(df: pd.DataFrame) -> plt.Figure:
    """
    Q3: ¿Más presupuesto garantiza más recaudación? ¿Varía por género?
    Scatter log-log. La diagonal representa ROI = 0 (break-even).
    """
    GENRES_SCATTER = ["Action", "Comedy", "Horror", "Animation", "Drama", "Thriller"]
    df_fin = df[df["roi"].notna()].copy()
    df_fin = df_fin[df_fin["primary_genre"].isin(GENRES_SCATTER)]

    palette = sns.color_palette("tab10", len(GENRES_SCATTER))
    color_map = dict(zip(GENRES_SCATTER, palette))

    fig, ax = plt.subplots(figsize=(11, 8))

    for genre in GENRES_SCATTER:
        subset = df_fin[df_fin["primary_genre"] == genre]
        ax.scatter(
            subset["budget"], subset["revenue"],
            label=genre, alpha=0.45, s=18,
            color=color_map[genre], linewidths=0
        )

    # Línea diagonal break-even
    lim = [1e5, 1.5e9]
    ax.plot(lim, lim, "--", color="#374151", linewidth=1.2, label="Break-even (ROI=0)", zorder=5)

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e6:.0f}M"))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x/1e6:.0f}M"))
    ax.set_xlabel("Presupuesto (escala log)", fontsize=11)
    ax.set_ylabel("Recaudación (escala log)", fontsize=11)
    ax.set_title(
        "Q3 · Presupuesto vs Recaudación por Género (escala log-log)\n"
        "Puntos sobre la diagonal = rentables; bajo la diagonal = pérdidas",
        fontsize=13, fontweight="bold", pad=15
    )
    ax.legend(title="Género", framealpha=0.9, fontsize=9)

    fig.tight_layout()
    _save(fig, "Q3_budget_vs_revenue.png")
    return fig


# ────────────────────────────────────────────────────────────────────────────
# Q4 — Valoración vs ROI (scatter + tendencia)
# ────────────────────────────────────────────────────────────────────────────
def plot_rating_vs_roi(df: pd.DataFrame) -> plt.Figure:
    """
    Q4: ¿Las películas mejor valoradas son también las más rentables?
    Scatter vote_average vs ROI con línea de tendencia LOWESS.
    ROI acotado al percentil 95 para evitar distorsión por outliers.
    """
    df_plot = df[df["roi"].notna()].copy()
    roi_cap = df_plot["roi"].quantile(0.95)
    df_plot = df_plot[df_plot["roi"] <= roi_cap]

    fig, ax = plt.subplots(figsize=(10, 7))

    # Scatter coloreado por tier
    tier_colors = {
        "Bajo":      "#DC2626",
        "Medio":     "#F59E0B",
        "Bueno":     "#2563EB",
        "Excelente": "#16A34A",
    }
    for tier, color in tier_colors.items():
        sub = df_plot[df_plot["rating_tier"] == tier]
        ax.scatter(sub["vote_average"], sub["roi"], color=color,
                   alpha=0.3, s=12, label=tier, linewidths=0)

    # Línea de tendencia (regresión polinómica grado 2)
    x = df_plot["vote_average"].values
    y = df_plot["roi"].values
    mask = np.isfinite(x) & np.isfinite(y)
    coefs = np.polyfit(x[mask], y[mask], deg=2)
    xfit = np.linspace(x[mask].min(), x[mask].max(), 200)
    yfit = np.polyval(coefs, xfit)
    ax.plot(xfit, yfit, color=PALETTE["secondary"], linewidth=2.5,
            label="Tendencia (poly-2)", zorder=10)

    ax.axhline(0, color="#374151", linewidth=1, linestyle="--", alpha=0.6)
    ax.set_xlabel("Valoración media (TMDB)", fontsize=11)
    ax.set_ylabel(f"ROI (cap. p95 ≈ {roi_cap:.1f}×)", fontsize=11)
    ax.set_title(
        "Q4 · Valoración de la Crítica vs Rentabilidad (ROI)\n"
        "Coloreado por tier de calidad; línea = tendencia cuadrática",
        fontsize=13, fontweight="bold", pad=15
    )
    ax.legend(title="Rating Tier", framealpha=0.9, fontsize=9)

    fig.tight_layout()
    _save(fig, "Q4_rating_vs_roi.png")
    return fig


# ────────────────────────────────────────────────────────────────────────────
# Q5 — Evolución temporal de la producción por género (líneas)
# ────────────────────────────────────────────────────────────────────────────
def plot_genre_trends(df: pd.DataFrame) -> plt.Figure:
    """
    Q5: ¿Qué géneros están en auge y podrían dominar la próxima década?
    Serie temporal 1980-2019 del número de producciones por género.
    Suavizado con media móvil de 3 años para reducir ruido.
    """
    TREND_GENRES = ["Action", "Animation", "Horror", "Science Fiction",
                    "Comedy", "Drama", "Thriller"]

    df_exp = explode_genres(df[df["release_year"].notna()])
    df_exp = df_exp[
        (df_exp["genre"].isin(TREND_GENRES)) &
        (df_exp["release_year"] >= 1980) &
        (df_exp["release_year"] <= 2019)
    ]

    pivot = (
        df_exp.groupby(["release_year", "genre"])
        .size()
        .unstack(fill_value=0)
    )
    # Media móvil 3 años
    pivot_smooth = pivot.rolling(3, center=True, min_periods=1).mean()

    palette = sns.color_palette("tab10", len(TREND_GENRES))

    fig, ax = plt.subplots(figsize=(13, 7))
    for genre, color in zip(TREND_GENRES, palette):
        if genre in pivot_smooth.columns:
            ax.plot(pivot_smooth.index, pivot_smooth[genre],
                    label=genre, color=color, linewidth=2.2, alpha=0.9)
            # Marcar el último punto
            last_y = pivot_smooth[genre].iloc[-1]
            ax.annotate(
                genre, xy=(2019, last_y), xytext=(5, 0),
                textcoords="offset points", va="center",
                fontsize=8, color=color
            )

    # Sombreado 2020+ = proyección
    ax.axvspan(2018, 2019, alpha=0.07, color="gray")
    ax.set_xlabel("Año de lanzamiento", fontsize=11)
    ax.set_ylabel("Número de producciones (media móvil 3 años)", fontsize=11)
    ax.set_title(
        "Q5 · Tendencias de Producción por Género (1980–2019)\n"
        "Géneros en auge sostenido = candidatos a dominar la próxima década",
        fontsize=13, fontweight="bold", pad=15
    )
    ax.legend(title="Género", loc="upper left", fontsize=9, framealpha=0.9)
    ax.set_xlim(1980, 2022)

    fig.tight_layout()
    _save(fig, "Q5_genre_trends.png")
    return fig


# ────────────────────────────────────────────────────────────────────────────
# Runner para generar todos los gráficos de una sola vez
# ────────────────────────────────────────────────────────────────────────────
def plot_all(df: pd.DataFrame) -> None:
    """Genera y guarda las 5 visualizaciones del proyecto."""
    print("\n[viz] Generando visualizaciones...")
    plot_roi_by_genre(df)
    plot_genre_decade_heatmap(df)
    plot_budget_vs_revenue(df)
    plot_rating_vs_roi(df)
    plot_genre_trends(df)
    print("[viz] ✓ Todas las visualizaciones guardadas en /figures/")
