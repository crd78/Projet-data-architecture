import os
from pathlib import Path

import geopandas as gpd
import pandas as pd
from dagster import (
    AssetExecutionContext,
    Definitions,
    MaterializeResult,
    MetadataValue,
    asset,
    define_asset_job,
)

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent / "datasets_finaux"
PIPELINE_DIR = Path(__file__).resolve().parent.parent.parent
PARQUET_BASE_DIR = PIPELINE_DIR / "datasets_finaux"

SOURCES = {
    "KPI_impose": PARQUET_BASE_DIR / "KPI_impose",
    "KPI_personnalise": PARQUET_BASE_DIR / "KPI_personnalise",
}

OUTPUT = {
    "KPI_impose": PARQUET_BASE_DIR / "KPI_impose_parquet",
    "KPI_personnalise": PARQUET_BASE_DIR / "KPI_personnalise_parquet",
}

SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".geojson"}


def read_dataset_file(filepath: Path) -> pd.DataFrame:
    ext = filepath.suffix.lower()
    if ext == ".csv":
        with open(filepath, "r", encoding="utf-8-sig") as f:
            first_line = f.readline()
        sep = ";" if first_line.count(";") > first_line.count(",") else ","
        return pd.read_csv(filepath, sep=sep, encoding="utf-8-sig", low_memory=False, on_bad_lines="skip")
    if ext == ".xlsx":
        return pd.read_excel(filepath)
    if ext == ".geojson":
        gdf = gpd.read_file(filepath)
        gdf["geometry"] = gdf["geometry"].astype(str)
        return pd.DataFrame(gdf)
    raise ValueError(f"Unsupported format: {ext}")


def _list_source_files(source_dir: Path) -> list[Path]:
    if not source_dir.exists():
        return []
    return sorted([p for p in source_dir.iterdir() if p.suffix.lower() in SUPPORTED_EXTENSIONS])


def _ingest_kpi_dataset(context: AssetExecutionContext, kpi_key: str) -> MaterializeResult:
    source_dir = SOURCES[kpi_key]
    output_dir = OUTPUT[kpi_key]
    source_dir.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(parents=True, exist_ok=True)

    files = _list_source_files(source_dir)
    processed = 0
    failed = 0
    total_rows = 0

    if not files:
        context.log.info(f"Aucun fichier source pour {kpi_key} dans {source_dir}")

    for source_path in files:
        stem = source_path.stem
        output_path = output_dir / f"{stem}.parquet"
        try:
            df = read_dataset_file(source_path)
            # Evite les erreurs parquet sur colonnes object heterogenes
            for col in df.select_dtypes(include="object").columns:
                df[col] = df[col].astype(str)

            df.to_parquet(output_path, index=False)
            processed += 1
            total_rows += len(df)
            context.log.info(f"{source_path.name} -> {output_path.name} ({len(df)} lignes)")
        except Exception as exc:
            failed += 1
            context.log.error(f"Erreur sur {source_path.name}: {exc}")

    return MaterializeResult(
        metadata={
            "kpi_key": kpi_key,
            "source_dir": MetadataValue.path(str(source_dir)),
            "output_dir": MetadataValue.path(str(output_dir)),
            "files_found": len(files),
            "files_processed": processed,
            "files_failed": failed,
            "rows_total": total_rows,
        }
    )


@asset(name="bronze_kpi_impose", group_name="bronze")
def bronze_kpi_impose(context: AssetExecutionContext) -> MaterializeResult:
    return _ingest_kpi_dataset(context, "KPI_impose")


@asset(name="bronze_kpi_personnalise", group_name="bronze")
def bronze_kpi_personnalise(context: AssetExecutionContext) -> MaterializeResult:
    return _ingest_kpi_dataset(context, "KPI_personnalise")


all_ingestion_assets = [bronze_kpi_impose, bronze_kpi_personnalise]

ingestion_job = define_asset_job(
    name="bronze_ingestion_job",
    selection=all_ingestion_assets,
)

defs = Definitions(
    assets=all_ingestion_assets,
    jobs=[ingestion_job],
)