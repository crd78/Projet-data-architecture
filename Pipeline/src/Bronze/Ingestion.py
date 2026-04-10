import os
from pathlib import Path
import pandas as pd
import geopandas as gpd

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent / "datasets_finaux"

SOURCES = {
    "KPI_impose": BASE_DIR / "KPI_impose",
    "KPI_personnalise": BASE_DIR / "KPI_personnalise",
}

OUTPUT = {
    "KPI_impose": BASE_DIR / "KPI_impose_parquet",
    "KPI_personnalise": BASE_DIR / "KPI_personnalise_parquet",
}

SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".geojson"}


def read_file(filepath: str) -> pd.DataFrame:
    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".csv":
        # Detect separator automatically
        with open(str(filepath), "r", encoding="utf-8-sig") as f:
            first_line = f.readline()
        sep = ";" if first_line.count(";") > first_line.count(",") else ","
        return pd.read_csv(filepath, sep=sep, encoding="utf-8-sig", low_memory=False, on_bad_lines="skip")
    elif ext == ".xlsx":
        return pd.read_excel(filepath)
    elif ext == ".geojson":
        gdf = gpd.read_file(filepath)
        # Convert geometry to WKT string for parquet compatibility
        gdf["geometry"] = gdf["geometry"].astype(str)
        return pd.DataFrame(gdf)
    else:
        raise ValueError(f"Unsupported format: {ext}")


def ingest():
    for kpi_key, source_dir in SOURCES.items():
        output_dir = OUTPUT[kpi_key]
        output_dir.mkdir(parents=True, exist_ok=True)

        files = [
            f for f in os.listdir(source_dir)
            if Path(f).suffix.lower() in SUPPORTED_EXTENSIONS
        ]

        print(f"\n[Bronze] Ingestion de {kpi_key} ({len(files)} fichiers)")

        for filename in files:
            filepath = source_dir / filename
            stem = Path(filename).stem
            output_path = output_dir / f"{stem}.parquet"

            try:
                df = read_file(filepath)
                # Fix mixed-type object columns (int + str) that break parquet serialization
                for col in df.select_dtypes(include="object").columns:
                    df[col] = df[col].astype(str)
                df.to_parquet(output_path, index=False)
                print(f"  OK  {filename} -> {stem}.parquet ({len(df)} lignes)")
            except Exception as e:
                print(f"  ERR {filename} : {e}")

    print("\n[Bronze] Ingestion terminee.")


if __name__ == "__main__":
    ingest()
