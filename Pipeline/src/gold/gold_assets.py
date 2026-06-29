import sqlite3
from pathlib import Path

import pandas as pd
from dagster import (
    AssetKey,
    AssetExecutionContext,
    MaterializeResult,
    MetadataValue,
    asset,
)

PIPELINE_DIR = Path(__file__).resolve().parent.parent.parent
BASE_DIR = PIPELINE_DIR / "datasets_finaux"
GOLD_DIR = BASE_DIR / "gold"
GOLD_DIR.mkdir(parents=True, exist_ok=True)

DB_PATH = BASE_DIR / "paris_immobilier.db"


def _read_table(table_name: str) -> pd.DataFrame:
    conn = sqlite3.connect(DB_PATH, timeout=60)
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
    finally:
        conn.close()
    return df


@asset(name="gold_quartiers_paris", group_name="gold", deps=[AssetKey("silver_quartiers")])
def quartiers_paris(context: AssetExecutionContext) -> MaterializeResult:
    from . import datamart

    datamart.quartiers_paris()
    df = _read_table("quartiers_paris")
    out = GOLD_DIR / "quartiers_paris.parquet"
    df.to_parquet(out, index=False)
    return MaterializeResult(metadata={"path": MetadataValue.path(str(out))})


@asset(
    name="gold_prix_arrondissement",
    group_name="gold",
    deps=[AssetKey("silver_kpi_impose_enriched"), AssetKey("gold_quartiers_paris")],
)
def prix_arrondissement(context: AssetExecutionContext) -> MaterializeResult:
    from . import datamart

    datamart.prix_arrondissement()
    df = _read_table("prix_arrondissement")
    out = GOLD_DIR / "prix_arrondissement.parquet"
    df.to_parquet(out, index=False)
    return MaterializeResult(metadata={"path": MetadataValue.path(str(out))})


@asset(
    name="gold_activite_quartier",
    group_name="gold",
    deps=[AssetKey("silver_kpi_personnalise_enriched"), AssetKey("gold_prix_arrondissement")],
)
def activite_quartier(context: AssetExecutionContext) -> MaterializeResult:
    from . import datamart

    datamart.activite_quartier()
    df = _read_table("activite_quartier")
    out = GOLD_DIR / "activite_quartier.parquet"
    df.to_parquet(out, index=False)
    return MaterializeResult(metadata={"path": MetadataValue.path(str(out))})


@asset(
    name="gold_nuisance_sonore",
    group_name="gold",
    deps=[AssetKey("silver_kpi_personnalise_enriched"), AssetKey("gold_activite_quartier")],
)
def nuisance_sonore(context: AssetExecutionContext) -> MaterializeResult:
    from . import datamart

    datamart.nuisance_sonore()
    df = _read_table("nuisance_sonore")
    out = GOLD_DIR / "nuisance_sonore.parquet"
    df.to_parquet(out, index=False)
    return MaterializeResult(metadata={"path": MetadataValue.path(str(out))})


@asset(
    name="gold_disponibilite_stationnement",
    group_name="gold",
    deps=[AssetKey("silver_kpi_personnalise_enriched"), AssetKey("gold_nuisance_sonore")],
)
def disponibilite_stationnement(context: AssetExecutionContext) -> MaterializeResult:
    from . import datamart

    datamart.disponibilite_stationnement()
    df = _read_table("disponibilite_stationnement")
    out = GOLD_DIR / "disponibilite_stationnement.parquet"
    df.to_parquet(out, index=False)
    return MaterializeResult(metadata={"path": MetadataValue.path(str(out))})


@asset(
    name="gold_proprete_general",
    group_name="gold",
    deps=[AssetKey("silver_kpi_personnalise_enriched"), AssetKey("gold_disponibilite_stationnement")],
)
def proprete_general(context: AssetExecutionContext) -> MaterializeResult:
    from . import datamart

    datamart.proprete_general()
    df = _read_table("proprete_general")
    out = GOLD_DIR / "proprete_general.parquet"
    df.to_parquet(out, index=False)
    return MaterializeResult(metadata={"path": MetadataValue.path(str(out))})


@asset(
    name="gold_population_niveau_vie",
    group_name="gold",
    deps=[AssetKey("silver_kpi_impose_enriched"), AssetKey("gold_proprete_general")],
)
def population_niveau_vie(context: AssetExecutionContext) -> MaterializeResult:
    from . import datamart

    datamart.population_niveau_vie()
    df = _read_table("population_niveau_vie")
    out = GOLD_DIR / "population_niveau_vie.parquet"
    df.to_parquet(out, index=False)
    return MaterializeResult(metadata={"path": MetadataValue.path(str(out))})


@asset(
    name="gold_logement_sociaux",
    group_name="gold",
    deps=[AssetKey("silver_kpi_impose_enriched"), AssetKey("gold_population_niveau_vie")],
)
def logement_sociaux(context: AssetExecutionContext) -> MaterializeResult:
    from . import datamart

    datamart.logement_sociaux()
    df = _read_table("logement_sociaux")
    out = GOLD_DIR / "logement_sociaux.parquet"
    df.to_parquet(out, index=False)
    return MaterializeResult(metadata={"path": MetadataValue.path(str(out))})


@asset(
    name="gold_location_arrondissement",
    group_name="gold",
    deps=[AssetKey("silver_kpi_impose_enriched"), AssetKey("gold_logement_sociaux")],
)
def location_arrondissement(context: AssetExecutionContext) -> MaterializeResult:
    from . import datamart

    datamart.location_arrondissement()
    df = _read_table("location_arrondissement")
    out = GOLD_DIR / "location_arrondissement.parquet"
    df.to_parquet(out, index=False)
    return MaterializeResult(metadata={"path": MetadataValue.path(str(out))})


all_gold_assets = [
    quartiers_paris,
    prix_arrondissement,
    activite_quartier,
    nuisance_sonore,
    disponibilite_stationnement,
    proprete_general,
    population_niveau_vie,
    logement_sociaux,
    location_arrondissement,
]
