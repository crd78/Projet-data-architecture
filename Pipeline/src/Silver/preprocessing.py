import json
import re
import unicodedata
from pathlib import Path

import pandas as pd
from dagster import (
    AssetExecutionContext,
    AssetKey,
    AssetSelection,
    Definitions,
    MaterializeResult,
    MetadataValue,
    asset,
    define_asset_job,
)
from shapely import wkt
from shapely.geometry import Point, shape
from shapely.prepared import prep

from executors import get_executor_def


PIPELINE_DIR = Path(__file__).resolve().parent.parent.parent
BASE_DIR = PIPELINE_DIR / "datasets_finaux"
SHOPCODE_DIR = PIPELINE_DIR / "ShopCode"

SOURCES = {
    "KPI_impose": BASE_DIR / "KPI_impose_parquet",
    "KPI_personnalise": BASE_DIR / "KPI_personnalise_parquet",
}

OUTPUT = {
    "KPI_impose": BASE_DIR / "KPI_impose_silver",
    "KPI_personnalise": BASE_DIR / "KPI_personnalise_silver",
}

ENRICHED_OUTPUT = {
    "KPI_impose": BASE_DIR / "KPI_impose_silver_enriched",
    "KPI_personnalise": BASE_DIR / "KPI_personnalise_silver_enriched",
}

QUARTIERS_SILVER_PATH = OUTPUT["KPI_impose"] / "quartiers_silver.parquet"

SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".geojson"}

CODEACT_CANDIDATE_COLUMNS = [
    "codeact",
    "code_act",
    "code_activite",
    "code_activite_principale",
    "codact",
]

DATE_COLUMNS = {
    "chantiers-a-paris-copie1": ["date_debut_du_chantier", "date_fin_du_chantier"],
    "dans-ma-rue": ["date_declaration"],
}

MULTIHEADER_FILES = {
    "BASE_TD_FILO_IRIS_2021_DEC",
    "base-ic-evol-struct-pop-2021",
}


def to_snake_case(col: str) -> str:
    text = unicodedata.normalize("NFD", str(col))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = re.sub(r"[^0-9a-zA-Z]+", "_", text)
    text = re.sub(r"_+", "_", text)
    return text.strip("_")


def _normalize_code(value) -> str:
    return str(value).strip().upper()


def _clean_missing_values(df: pd.DataFrame) -> pd.DataFrame:
    return df.replace(
        {
            "nan": pd.NA,
            "NaN": pd.NA,
            "None": pd.NA,
            "NaT": pd.NA,
            "<NA>": pd.NA,
            "": pd.NA,
        }
    )


def load_allowed_codeact() -> set[str]:
    allowed = set()
    for filepath in [SHOPCODE_DIR / "CodeEtablissement2023.json"]:
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


def parse_geo_point(value) -> tuple[float | None, float | None]:
    if value is None or pd.isna(value):
        return None, None
    text = str(value).strip()
    if not text:
        return None, None

    numbers = re.findall(r"-?\d+(?:[.,]\d+)?", text)
    if len(numbers) < 2:
        return None, None

    try:
        latitude = float(numbers[0].replace(",", "."))
        longitude = float(numbers[1].replace(",", "."))
    except ValueError:
        return None, None

    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return None, None
    return latitude, longitude


def split_geo_point(df: pd.DataFrame) -> pd.DataFrame:
    if "geo_point_2d" not in df.columns:
        return df

    coords = df["geo_point_2d"].apply(parse_geo_point)
    df["latitude"] = pd.to_numeric(coords.map(lambda pair: pair[0]), errors="coerce")
    df["longitude"] = pd.to_numeric(coords.map(lambda pair: pair[1]), errors="coerce")
    df = df.drop(columns=["geo_point_2d"])
    return df


def extract_arrondissement(df: pd.DataFrame) -> pd.DataFrame:
    for candidate in [
        "arrondissement",
        "arro",
        "code_postal_arrondissement_commune",
        "code_postal",
        "insee",
    ]:
        if candidate not in df.columns:
            continue

        raw = df[candidate].astype("string")
        numeric = pd.to_numeric(raw.str.replace(r"\.0$", "", regex=True), errors="coerce")

        if candidate in {"arrondissement", "arro"} and numeric.notna().any():
            values = numeric.astype("Int64")
            if values.dropna().between(1, 20).all():
                df["arrondissement"] = values
                return df

        arr_from_750 = raw.str.extract(r"750(\d{2})")[0]
        if arr_from_750.notna().any():
            df["arrondissement"] = pd.to_numeric(arr_from_750, errors="coerce").astype("Int64")
            return df

        arr_from_751 = raw.str.extract(r"751(\d{2})")[0]
        if arr_from_751.notna().any():
            df["arrondissement"] = pd.to_numeric(arr_from_751, errors="coerce").astype("Int64")
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
    df = _clean_missing_values(df)

    if ALLOWED_CODEACT:
        code_col = next((col for col in CODEACT_CANDIDATE_COLUMNS if col in df.columns), None)
        if code_col is not None:
            normalized = df[code_col].astype("string").str.strip().str.upper()
            df = df[normalized.isin(ALLOWED_CODEACT)]

    for date_col in date_columns_for(stem):
        if date_col in df.columns:
            df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

    for col in ["code_postal", "code_postal_arrondissement_commune", "insee"]:
        if col in df.columns:
            df[col] = df[col].astype("string").str.replace(r"\.0$", "", regex=True)

    df = split_geo_point(df)
    df = extract_arrondissement(df)
    df = df.drop_duplicates()

    final_rows = len(df)
    return df, initial_rows, final_rows


def _preprocess_kpi_dataset(context: AssetExecutionContext, kpi_key: str) -> MaterializeResult:
    source_dir = SOURCES[kpi_key]
    output_dir = OUTPUT[kpi_key]
    output_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(source_dir.glob("*.parquet"))
    processed = skipped = failed = rows_in = rows_out = 0

    if not files:
        raise FileNotFoundError(f"Aucun fichier parquet Silver source dans {source_dir}")

    for filepath in files:
        stem = filepath.stem
        output_path = output_dir / filepath.name

        if stem.startswith("meta_"):
            skipped += 1
            continue

        try:
            df = pd.read_parquet(filepath)
            df, initial, final = preprocess_file(stem, df)
            df.to_parquet(output_path, index=False)

            processed += 1
            rows_in += initial
            rows_out += final
            context.log.info(f"{filepath.name} | {initial} -> {final}")
        except Exception as exc:
            failed += 1
            context.log.error(f"Erreur preprocessing {filepath.name}: {exc}")

    if failed:
        raise RuntimeError(f"{failed} fichier(s) Silver en erreur pour {kpi_key}")

    return MaterializeResult(
        metadata={
            "kpi_key": kpi_key,
            "output_dir": MetadataValue.path(str(output_dir)),
            "files_found": len(files),
            "files_processed": processed,
            "files_skipped": skipped,
            "files_failed": failed,
            "rows_input_total": rows_in,
            "rows_output_total": rows_out,
        }
    )


def _parse_geometry(value):
    if value is None or pd.isna(value):
        return None
    if hasattr(value, "__geo_interface__"):
        return value

    text = str(value).strip()
    if not text:
        return None

    try:
        if text.startswith("{") or text.startswith("["):
            payload = json.loads(text)
            if isinstance(payload, dict):
                return shape(payload)
        return wkt.loads(text)
    except Exception:
        return None


def _build_quartiers_lookup(df: pd.DataFrame) -> pd.DataFrame:
    required = ["c_qu", "c_quinsee", "l_qu", "c_ar", "surface", "geometry"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise KeyError(f"Colonnes manquantes dans quartier_paris: {missing}")

    lookup = df[required].copy()
    lookup = lookup.rename(
        columns={
            "c_qu": "num_quartier",
            "c_quinsee": "code_quartier_insee",
            "l_qu": "nom_quartier",
            "c_ar": "arrondissement_quartier",
            "surface": "surface_quartier",
            "geometry": "geometry_quartier",
        }
    )
    lookup["num_quartier"] = pd.to_numeric(lookup["num_quartier"], errors="coerce").astype("Int64")
    lookup["arrondissement_quartier"] = pd.to_numeric(
        lookup["arrondissement_quartier"], errors="coerce"
    ).astype("Int64")
    lookup["code_quartier_insee"] = lookup["code_quartier_insee"].astype("string")
    lookup["surface_quartier"] = pd.to_numeric(lookup["surface_quartier"], errors="coerce")
    lookup["geometry_quartier"] = lookup["geometry_quartier"].astype("string")
    lookup = lookup.dropna(subset=["num_quartier", "nom_quartier", "geometry_quartier"])
    return lookup.drop_duplicates("num_quartier").reset_index(drop=True)


def _quartier_zones(lookup: pd.DataFrame) -> list[dict]:
    zones = []
    for _, row in lookup.iterrows():
        geom = _parse_geometry(row["geometry_quartier"])
        if geom is None or geom.is_empty:
            continue
        zones.append(
            {
                "num_quartier": row["num_quartier"],
                "nom_quartier": row["nom_quartier"],
                "arrondissement_quartier": row["arrondissement_quartier"],
                "surface_quartier": row["surface_quartier"],
                "geometry_quartier": row["geometry_quartier"],
                "bounds": geom.bounds,
                "prepared": prep(geom),
            }
        )
    return zones


def _normalize_join_key(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype("string").str.replace(r"\.0$", "", regex=True), errors="coerce")


def _add_quartier_by_code(df: pd.DataFrame, lookup: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    lookup_by_num = lookup.copy()
    lookup_by_num["_join_quartier"] = lookup_by_num["num_quartier"].astype("Int64")

    code_candidates = ["num_quartier", "qua", "numero_du_quartier"]
    for candidate in code_candidates:
        if candidate not in df.columns:
            continue
        df["_join_quartier"] = _normalize_join_key(df[candidate]).astype("Int64")
        df = df.merge(
            lookup_by_num[
                [
                    "_join_quartier",
                    "nom_quartier",
                    "arrondissement_quartier",
                    "surface_quartier",
                    "geometry_quartier",
                ]
            ],
            on="_join_quartier",
            how="left",
            suffixes=("", "_lookup"),
        )
        df["num_quartier"] = df.get("num_quartier", df["_join_quartier"]).fillna(df["_join_quartier"])
        for col in ["nom_quartier", "arrondissement_quartier", "surface_quartier", "geometry_quartier"]:
            lookup_col = f"{col}_lookup"
            if lookup_col in df.columns:
                if col in df.columns:
                    df[col] = df[col].fillna(df[lookup_col])
                else:
                    df[col] = df[lookup_col]
                df = df.drop(columns=[lookup_col])
        df = df.drop(columns=["_join_quartier"])
        return df

    if "numero_insee_du_quartier" in df.columns:
        lookup_by_insee = lookup.copy()
        lookup_by_insee["_join_insee"] = lookup_by_insee["code_quartier_insee"].astype("string")
        df["_join_insee"] = df["numero_insee_du_quartier"].astype("string").str.replace(r"\.0$", "", regex=True)
        df = df.merge(
            lookup_by_insee[
                [
                    "_join_insee",
                    "num_quartier",
                    "nom_quartier",
                    "arrondissement_quartier",
                    "surface_quartier",
                    "geometry_quartier",
                ]
            ],
            on="_join_insee",
            how="left",
            suffixes=("", "_lookup"),
        )
        for col in ["num_quartier", "nom_quartier", "arrondissement_quartier", "surface_quartier", "geometry_quartier"]:
            lookup_col = f"{col}_lookup"
            if lookup_col in df.columns:
                df[col] = df[col].fillna(df[lookup_col]) if col in df.columns else df[lookup_col]
                df = df.drop(columns=[lookup_col])
        df = df.drop(columns=["_join_insee"])

    return df


def _locate_quartier(row: pd.Series, zones: list[dict]) -> tuple[object, object, object, object, object]:
    latitude = row.get("latitude")
    longitude = row.get("longitude")
    if pd.isna(latitude) or pd.isna(longitude):
        return pd.NA, pd.NA, pd.NA, pd.NA, pd.NA

    arrondissement = row.get("arrondissement")
    if pd.isna(arrondissement):
        arrondissement = None

    point = Point(float(longitude), float(latitude))
    for zone in zones:
        if arrondissement is not None and zone["arrondissement_quartier"] != int(arrondissement):
            continue
        minx, miny, maxx, maxy = zone["bounds"]
        if not (minx <= point.x <= maxx and miny <= point.y <= maxy):
            continue
        if zone["prepared"].covers(point):
            return (
                zone["num_quartier"],
                zone["nom_quartier"],
                zone["arrondissement_quartier"],
                zone["surface_quartier"],
                zone["geometry_quartier"],
            )
    return pd.NA, pd.NA, pd.NA, pd.NA, pd.NA


def enrich_with_quartiers(df: pd.DataFrame, lookup: pd.DataFrame) -> pd.DataFrame:
    df = _add_quartier_by_code(df, lookup)

    for col in ["num_quartier", "nom_quartier", "arrondissement_quartier", "surface_quartier", "geometry_quartier"]:
        if col not in df.columns:
            df[col] = pd.NA

    if "latitude" not in df.columns or "longitude" not in df.columns:
        return df

    missing = df["num_quartier"].isna() & df["latitude"].notna() & df["longitude"].notna()
    if not missing.any():
        return df

    zones = _quartier_zones(lookup)
    located = df.loc[missing].apply(lambda row: _locate_quartier(row, zones), axis=1, result_type="expand")
    located.columns = [
        "num_quartier",
        "nom_quartier",
        "arrondissement_quartier",
        "surface_quartier",
        "geometry_quartier",
    ]

    for col in located.columns:
        df.loc[missing, col] = located[col].values

    return df


def _enrich_kpi_dataset(context: AssetExecutionContext, kpi_key: str) -> MaterializeResult:
    source_dir = OUTPUT[kpi_key]
    output_dir = ENRICHED_OUTPUT[kpi_key]
    output_dir.mkdir(parents=True, exist_ok=True)

    if not QUARTIERS_SILVER_PATH.exists():
        raise FileNotFoundError(f"Table quartiers Silver manquante: {QUARTIERS_SILVER_PATH}")

    lookup = pd.read_parquet(QUARTIERS_SILVER_PATH)
    files = sorted(source_dir.glob("*.parquet"))
    processed = failed = rows_total = rows_with_quartier = 0

    if not files:
        raise FileNotFoundError(f"Aucun fichier Silver a enrichir dans {source_dir}")

    for filepath in files:
        try:
            df = pd.read_parquet(filepath)
            df = enrich_with_quartiers(df, lookup)
            output_path = output_dir / filepath.name
            df.to_parquet(output_path, index=False)

            processed += 1
            rows_total += len(df)
            if "num_quartier" in df.columns:
                rows_with_quartier += int(df["num_quartier"].notna().sum())
            context.log.info(f"{filepath.name} enrichi -> {output_path.name}")
        except Exception as exc:
            failed += 1
            context.log.error(f"Erreur enrichissement {filepath.name}: {exc}")

    if failed:
        raise RuntimeError(f"{failed} fichier(s) Silver enrichi en erreur pour {kpi_key}")

    return MaterializeResult(
        metadata={
            "kpi_key": kpi_key,
            "source_dir": MetadataValue.path(str(source_dir)),
            "output_dir": MetadataValue.path(str(output_dir)),
            "files_processed": processed,
            "rows_total": rows_total,
            "rows_with_quartier": rows_with_quartier,
        }
    )


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


@asset(
    name="silver_quartiers",
    group_name="silver",
    deps=[AssetKey("silver_kpi_impose")],
)
def silver_quartiers(context: AssetExecutionContext) -> MaterializeResult:
    quartiers_path = OUTPUT["KPI_impose"] / "quartier_paris.parquet"
    if not quartiers_path.exists():
        raise FileNotFoundError(f"Fichier quartiers non trouve: {quartiers_path}")

    df = pd.read_parquet(quartiers_path)
    lookup = _build_quartiers_lookup(df)
    QUARTIERS_SILVER_PATH.parent.mkdir(parents=True, exist_ok=True)
    lookup.to_parquet(QUARTIERS_SILVER_PATH, index=False)

    return MaterializeResult(
        metadata={
            "path": MetadataValue.path(str(QUARTIERS_SILVER_PATH)),
            "rows": len(lookup),
        }
    )


@asset(
    name="silver_kpi_impose_enriched",
    group_name="silver",
    deps=[AssetKey("silver_kpi_impose"), AssetKey("silver_quartiers")],
)
def silver_kpi_impose_enriched(context: AssetExecutionContext) -> MaterializeResult:
    return _enrich_kpi_dataset(context, "KPI_impose")


@asset(
    name="silver_kpi_personnalise_enriched",
    group_name="silver",
    deps=[AssetKey("silver_kpi_personnalise"), AssetKey("silver_quartiers")],
)
def silver_kpi_personnalise_enriched(context: AssetExecutionContext) -> MaterializeResult:
    return _enrich_kpi_dataset(context, "KPI_personnalise")


all_preprocessing_assets = [
    silver_kpi_impose,
    silver_kpi_personnalise,
    silver_quartiers,
    silver_kpi_impose_enriched,
    silver_kpi_personnalise_enriched,
]

preprocessing_job = define_asset_job(
    name="silver_preprocessing_job",
    selection=AssetSelection.assets(*all_preprocessing_assets),
    executor_def=get_executor_def(),
)

defs = Definitions(
    assets=all_preprocessing_assets,
    jobs=[preprocessing_job],
)


def preprocess():
    for kpi_key, source_dir in SOURCES.items():
        output_dir = OUTPUT[kpi_key]
        output_dir.mkdir(parents=True, exist_ok=True)

        files = sorted(source_dir.glob("*.parquet"))
        print(f"\n[Silver] {kpi_key} ({len(files)} fichiers)")

        for filepath in files:
            stem = filepath.stem
            if stem.startswith("meta_"):
                continue

            df = pd.read_parquet(filepath)
            df, initial, final = preprocess_file(stem, df)
            df.to_parquet(output_dir / filepath.name, index=False)
            print(f"{filepath.name} | {initial} -> {final}")

    quartiers_df = pd.read_parquet(OUTPUT["KPI_impose"] / "quartier_paris.parquet")
    _build_quartiers_lookup(quartiers_df).to_parquet(QUARTIERS_SILVER_PATH, index=False)

    lookup = pd.read_parquet(QUARTIERS_SILVER_PATH)
    for kpi_key in SOURCES:
        output_dir = ENRICHED_OUTPUT[kpi_key]
        output_dir.mkdir(parents=True, exist_ok=True)
        for filepath in sorted(OUTPUT[kpi_key].glob("*.parquet")):
            df = enrich_with_quartiers(pd.read_parquet(filepath), lookup)
            df.to_parquet(output_dir / filepath.name, index=False)


if __name__ == "__main__":
    preprocess()
