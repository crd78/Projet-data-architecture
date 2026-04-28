import unicodedata
import re
import json
from pathlib import Path

import pandas as pd
from dagster import (
    AssetSelection,
    AssetKey,
    AssetExecutionContext,
    Definitions,
    MaterializeResult,
    MetadataValue,
    asset,
    define_asset_job,
)

# ─── Chemins ───────────────────────────────────────────────────────────────────

PIPELINE_DIR = Path(__file__).resolve().parent.parent.parent
BASE_DIR     = PIPELINE_DIR / "datasets_finaux"
SHOPCODE_DIR = PIPELINE_DIR / "ShopCode"

SOURCES = {
    "KPI_impose":       BASE_DIR / "KPI_impose_parquet",
    "KPI_personnalise": BASE_DIR / "KPI_personnalise_parquet",
}

OUTPUT = {
    "KPI_impose":       BASE_DIR / "KPI_impose_silver",
    "KPI_personnalise": BASE_DIR / "KPI_personnalise_silver",
}

TARGET_FILE = "BDCOM_2023.parquet"

# ─── Référentiels codeact ──────────────────────────────────────────────────────

CODEACT_CANDIDATE_COLUMNS = [
    "codeact",
    "code_act",
    "code_activite",
    "code_activite_principale",
]

DATE_COLUMNS = {
    "chantiers-a-paris-copie1": ["date_debut_du_chantier", "date_fin_du_chantier"],
    "dans-ma-rue":              ["date_declaration"],
}

MULTIHEADER_FILES = {
    "BASE_TD_FILO_IRIS_2021_DEC",
    "base-ic-evol-struct-pop-2021",
}


def _normalize_code(value: str) -> str:
    return str(value).strip().upper()


def load_allowed_codeact() -> set[str]:
    allowed = set()
    json_files = [
        SHOPCODE_DIR / "CodeEtablissement2023.json",
    ]
    for filepath in json_files:
        if not filepath.exists():
            continue
        with open(filepath, "r", encoding="utf-8") as f:
            payload = json.load(f)
        for categories in payload.values():
            if not isinstance(categories, list):
                continue
            for category in categories:
                for item in category.get("items", []):
                    for code in item.get("codes", []):
                        allowed.add(_normalize_code(code))
                for code_item in category.get("codes", []):
                    code = code_item.get("code")
                    if code:
                        allowed.add(_normalize_code(code))
    return allowed


ALLOWED_CODEACT = load_allowed_codeact()

# ─── Helpers Silver ────────────────────────────────────────────────────────────

def to_snake_case(col: str) -> str:
    col = unicodedata.normalize("NFD", str(col))
    col = col.encode("ascii", "ignore").decode("ascii")
    col = col.lower().strip()
    col = re.sub(r"[^\w\s]", "", col)
    col = re.sub(r"\s+", "_", col)
    col = re.sub(r"_+", "_", col)
    return col


def split_geo_point(df: pd.DataFrame) -> pd.DataFrame:
    col = "geo_point_2d"
    if col not in df.columns:
        return df
    coords = df[col].str.split(",", expand=True)
    if coords.shape[1] >= 2:
        df["latitude"]  = pd.to_numeric(coords[0].str.strip(), errors="coerce")
        df["longitude"] = pd.to_numeric(coords[1].str.strip(), errors="coerce")
    df = df.drop(columns=[col])
    return df


def extract_arrondissement(df: pd.DataFrame) -> pd.DataFrame:
    for candidate in ["code_postal_arrondissement__commune", "code_postal", "arrondissement"]:
        if candidate in df.columns:
            numeric = pd.to_numeric(df[candidate], errors="coerce")
            if (
                candidate == "arrondissement"
                and numeric.notna().any()
                and numeric.dropna().between(1, 20).all()
            ):
                df["arrondissement"] = numeric.astype("Int64")
                return df
            series = df[candidate].astype("string").str.extract(r"750(\d{2})")[0]
            if series.notna().any():
                df["arrondissement"] = pd.to_numeric(series, errors="coerce").astype("Int64")
                return df
    return df


def fix_multiheader(df: pd.DataFrame) -> pd.DataFrame:
    if len(df) < 6:
        raise ValueError("Fichier multi-entete trop court pour etre normalise")
    new_cols = df.iloc[4].tolist()
    df = df.iloc[5:].copy()
    df.columns = [str(c) for c in new_cols]
    df = df.reset_index(drop=True)
    for col in df.columns:
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().sum() > 0:
            df[col] = converted
    return df


def date_columns_for(stem: str) -> list[str]:
    for file_stem, columns in DATE_COLUMNS.items():
        if stem == file_stem or stem.startswith(f"{file_stem}-"):
            return columns
    return []


def preprocess_file(stem: str, df: pd.DataFrame) -> tuple[pd.DataFrame, int, int]:
    initial_rows = len(df)

    if stem in MULTIHEADER_FILES:
        df = fix_multiheader(df)

    df.columns = [to_snake_case(c) for c in df.columns]

    if ALLOWED_CODEACT:
        code_col = next((col for col in CODEACT_CANDIDATE_COLUMNS if col in df.columns), None)
        if code_col is not None:
            normalized = df[code_col].astype(str).str.strip().str.upper()
            df = df[normalized.isin(ALLOWED_CODEACT)]

    for date_col in date_columns_for(stem):
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    for col in ["code_postal", "code_postal_arrondissement__commune"]:
        if col in df.columns:
            df[col] = df[col].astype("string").str.replace(r"\.0$", "", regex=True)

    df = split_geo_point(df)
    df = df.drop_duplicates()
    df = extract_arrondissement(df)

    final_rows = len(df)
    return df, initial_rows, final_rows


def _preprocess_kpi_dataset(context: AssetExecutionContext, kpi_key: str) -> MaterializeResult:
    source_dir = SOURCES[kpi_key]
    output_dir = OUTPUT[kpi_key]
    output_dir.mkdir(parents=True, exist_ok=True)

    files      = list(source_dir.glob("*.parquet"))
    processed  = skipped = failed = rows_in = rows_out = 0

    if not files:
        raise FileNotFoundError(f"Aucun fichier parquet Silver source dans {source_dir}")

    for filepath in files:
        stem        = filepath.stem
        output_path = output_dir / filepath.name

        if stem.startswith("meta_"):
            skipped += 1
            continue

        try:
            df = pd.read_parquet(filepath)
            df, initial, final = preprocess_file(stem, df)

            # ✅ PLUS AUCUN ENRICHISSEMENT ICI
            df.to_parquet(output_path, index=False)

            processed += 1
            rows_in   += initial
            rows_out  += final

            context.log.info(f"{filepath.name} | {initial} -> {final}")

        except Exception as exc:
            failed += 1
            context.log.error(f"Erreur preprocessing {filepath.name}: {exc}")

    if failed:
        raise RuntimeError(f"{failed} fichier(s) Silver en erreur pour {kpi_key}")

    return MaterializeResult(
        metadata={
            "kpi_key":           kpi_key,
            "files_found":       len(files),
            "files_processed":   processed,
            "files_skipped":     skipped,
            "files_failed":      failed,
            "rows_input_total":  rows_in,
            "rows_output_total": rows_out,
        }
    )

# ─── Assets Silver ─────────────────────────────────────────────────────────────

@asset(
    name="silver_kpi_impose",
    group_name="silver",
    deps=[AssetKey("bronze_kpi_impose")],
)
def silver_kpi_impose(context: AssetExecutionContext) -> MaterializeResult:
    return _preprocess_kpi_dataset(context, "KPI_impose")


@asset(
    name="silver_kpi_personnalise",
    group_name="silver",
    deps=[AssetKey("bronze_kpi_personnalise")],
)
def silver_kpi_personnalise(context: AssetExecutionContext) -> MaterializeResult:
    return _preprocess_kpi_dataset(context, "KPI_personnalise")

# ─── Jobs ──────────────────────────────────────────────────────────────────────

all_preprocessing_assets = [silver_kpi_impose, silver_kpi_personnalise]

preprocessing_job = define_asset_job(
    name="silver_preprocessing_job",
    selection=AssetSelection.assets(*all_preprocessing_assets),
)

defs = Definitions(
    assets=all_preprocessing_assets,
    jobs=[preprocessing_job],
)

# ─── Standalone ───────────────────────────────────────────────────────────────

def preprocess():
    for kpi_key, source_dir in SOURCES.items():
        output_dir = OUTPUT[kpi_key]
        output_dir.mkdir(parents=True, exist_ok=True)

        files = list(source_dir.glob("*.parquet"))
        print(f"\n[Silver] {kpi_key} ({len(files)} fichiers)")

        for filepath in files:
            stem = filepath.stem
            output_path = output_dir / filepath.name

            if stem.startswith("meta_"):
                continue

            df = pd.read_parquet(filepath)
            df, initial, final = preprocess_file(stem, df)
            df.to_parquet(output_path, index=False)

            print(f"{filepath.name} | {initial} → {final}")

if __name__ == "__main__":
    preprocess()
