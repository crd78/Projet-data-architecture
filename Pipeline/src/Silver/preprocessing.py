import os
import unicodedata
import re
from pathlib import Path

import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent / "datasets_finaux"

SOURCES = {
    "KPI_impose": BASE_DIR / "KPI_impose_parquet",
    "KPI_personnalise": BASE_DIR / "KPI_personnalise_parquet",
}

OUTPUT = {
    "KPI_impose": BASE_DIR / "KPI_impose_silver",
    "KPI_personnalise": BASE_DIR / "KPI_personnalise_silver",
}

# Colonnes date par fichier (après snake_case)
DATE_COLUMNS = {
    "chantiers-a-paris-copie1": ["date_debut_du_chantier", "date_fin_du_chantier"],
    "dans-ma-rue": ["date_declaration"],
}

# Fichiers xlsx avec multi-en-tête : la vraie ligne d'en-tête est à l'index 4
MULTIHEADER_FILES = {
    "BASE_TD_FILO_IRIS_2021_DEC",
    "base-ic-evol-struct-pop-2021",
}

# ─── Helpers ───────────────────────────────────────────────────────────────────

def to_snake_case(col: str) -> str:
    """Convertit un nom de colonne en snake_case sans accents."""
    col = unicodedata.normalize("NFD", str(col))
    col = col.encode("ascii", "ignore").decode("ascii")
    col = col.lower().strip()
    col = re.sub(r"[^\w\s]", "", col)
    col = re.sub(r"\s+", "_", col)
    col = re.sub(r"_+", "_", col)
    return col


def split_geo_point(df: pd.DataFrame) -> pd.DataFrame:
    """Extrait latitude et longitude depuis la colonne geo_point_2d."""
    col = "geo_point_2d"
    if col not in df.columns:
        return df
    coords = df[col].str.split(",", expand=True)
    if coords.shape[1] >= 2:
        df["latitude"] = pd.to_numeric(coords[0].str.strip(), errors="coerce")
        df["longitude"] = pd.to_numeric(coords[1].str.strip(), errors="coerce")
    df = df.drop(columns=[col])
    return df


def extract_arrondissement(df: pd.DataFrame) -> pd.DataFrame:
    """Ajoute une colonne arrondissement (1-20) depuis le code postal si disponible."""
    for candidate in ["code_postal_arrondissement__commune", "code_postal", "arrondissement"]:
        if candidate in df.columns:
            if candidate == "arrondissement" and df[candidate].dtype in ["int64", "float64"]:
                df["arrondissement"] = df[candidate].astype("Int64")
                return df
            series = df[candidate].astype(str).str.extract(r"750(\d{2})")[0]
            if series.notna().any():
                df["arrondissement"] = pd.to_numeric(series, errors="coerce").astype("Int64")
                return df
    return df


# ─── Étape 2 — Correction fichiers multi-en-tête ──────────────────────────────

def fix_multiheader(df: pd.DataFrame) -> pd.DataFrame:
    """
    Pour les xlsx lus avec pandas sans header correct :
    - row 3 = noms lisibles, row 4 = codes techniques
    - data à partir de row 5
    """
    new_cols = df.iloc[4].tolist()          # codes techniques (ex: DEC_PIMP21, IRIS…)
    df = df.iloc[5:].copy()
    df.columns = [str(c) for c in new_cols]
    df = df.reset_index(drop=True)

    # Cast colonnes numériques (garde la valeur originale si non convertible)
    for col in df.columns:
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().sum() > 0:
            df[col] = converted

    return df


# ─── Pipeline principal ────────────────────────────────────────────────────────

def preprocess_file(stem: str, df: pd.DataFrame) -> pd.DataFrame:
    initial_rows = len(df)

    # Étape 2 — multi-en-tête
    if stem in MULTIHEADER_FILES:
        df = fix_multiheader(df)

    # Étape 1 — snake_case
    df.columns = [to_snake_case(c) for c in df.columns]

    # Étape 3 — Nettoyage nulls spécifique
    if stem in {"BASE_TD_FILO_DEC_IRIS_2018", "BASE_TD_FILO_DEC_IRIS_2019", "BASE_TD_FILO_DEC_IRIS_2020"}:
        indicator_cols = [c for c in df.columns if c != "iris"]
        df = df.dropna(subset=indicator_cols, how="all")

    elif stem == "chantiers-a-paris-copie1":
        # Supprimer lignes sans référence ni date
        df = df.dropna(subset=["reference_chantier", "date_debut_du_chantier"], how="any")
        # Supprimer colonnes avec >80% nulls
        threshold = 0.8
        df = df.loc[:, df.isnull().mean() <= threshold]

    elif stem == "logements-sociaux-finances-a-paris":
        if "commentaires" in df.columns:
            df = df.drop(columns=["commentaires"])

    elif stem == "stationnement-parking-public":
        df = df.loc[:, df.isnull().mean() <= 0.8]

    # Étape 4 — Typage dates
    for date_col in DATE_COLUMNS.get(stem, []):
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    # Étape 4 — Code postal en str
    for col in ["code_postal", "code_postal_arrondissement__commune"]:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(r"\.0$", "", regex=True)

    # Étape 4 — geo_point_2d → latitude / longitude
    df = split_geo_point(df)

    # Étape 5 — Dédoublonnage
    df = df.drop_duplicates()

    # Étape 6 — Harmonisation arrondissement
    df = extract_arrondissement(df)

    final_rows = len(df)
    return df, initial_rows, final_rows


def preprocess():
    for kpi_key, source_dir in SOURCES.items():
        output_dir = OUTPUT[kpi_key]
        output_dir.mkdir(parents=True, exist_ok=True)

        files = list(source_dir.glob("*.parquet"))
        print(f"\n[Silver] Preprocessing {kpi_key} ({len(files)} fichiers)")

        for filepath in files:
            stem = filepath.stem
            output_path = output_dir / filepath.name

            # Ignorer les fichiers meta
            if stem.startswith("meta_"):
                print(f"  SKIP {filepath.name} (metadata)")
                continue

            try:
                df = pd.read_parquet(filepath)
                df, initial, final = preprocess_file(stem, df)
                df.to_parquet(output_path, index=False)
                print(f"  OK   {filepath.name} | {initial} → {final} lignes ({initial - final} supprimees)")
            except Exception as e:
                print(f"  ERR  {filepath.name} : {e}")

    print("\n[Silver] Preprocessing termine.")


if __name__ == "__main__":
    preprocess()
