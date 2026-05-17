"""
main.py — Entrypoint reproducible del proyecto.
Pipeline completo: load → clean → features → export → visualize

Uso:
    python main.py
"""
import sys
from pathlib import Path

# Garantiza que la raíz del proyecto esté en el path
sys.path.insert(0, str(Path(__file__).parent))

from src.io       import load_csv, export_csv
from src.cleaning import clean
from src.features import build_features
from src.viz      import plot_all
from src.config   import RAW_PATH, OUT_PATH


def run_pipeline() -> None:
    print("=" * 60)
    print("  TMDB Movie Analytics — Pipeline Reproducible")
    print("  Máster en Data Science & AI")
    print("=" * 60)

    # 1. Carga ─────────────────────────────────────────────────────
    print("\n[1/5] Cargando datos crudos...")
    df = load_csv(RAW_PATH)
    print(f"      {len(df):,} filas · {df.shape[1]} columnas")

    # 2. Limpieza ──────────────────────────────────────────────────
    print("\n[2/5] Aplicando limpieza y transformaciones...")
    df = clean(df)

    # 3. Features ──────────────────────────────────────────────────
    print("\n[3/5] Construyendo features...")
    df = build_features(df)

    # 4. Exportar ──────────────────────────────────────────────────
    print("\n[4/5] Exportando dataset limpio...")
    export_csv(df, OUT_PATH)

    # 5. Visualizaciones ───────────────────────────────────────────
    print("\n[5/5] Generando visualizaciones...")
    plot_all(df)

    print("\n" + "=" * 60)
    print("  Pipeline completado con éxito.")
    print(f"  Dataset limpio → {OUT_PATH}")
    print(f"  Gráficos       → figures/")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()
