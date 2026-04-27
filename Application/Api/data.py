from functools import lru_cache
from pathlib import Path

import pandas as pd

SILVER_IMPOSE = Path(__file__).resolve().parents[2] / "Pipeline" / "datasets_finaux" / "KPI_impose_silver"
SILVER_PERSO = Path(__file__).resolve().parents[2] / "Pipeline" / "datasets_finaux" / "KPI_personnalise_silver"


@lru_cache(maxsize=None)
def load(filename: str, layer: str = "impose") -> pd.DataFrame:
    base = SILVER_IMPOSE if layer == "impose" else SILVER_PERSO
    path = base / f"{filename}.parquet"
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    return pd.read_parquet(path)


def quartiers() -> pd.DataFrame:
    return load("quartier_paris")


def logements_sociaux() -> pd.DataFrame:
    return load("logements-sociaux-finances-a-paris")


def loyers() -> pd.DataFrame:
    return load("logement-encadrement-des-loyers")


def revenus_iris(annee: int) -> pd.DataFrame:
    return load(f"BASE_TD_FILO_DEC_IRIS_{annee}")


def population() -> pd.DataFrame:
    return load("base-ic-evol-struct-pop-2021")


def chantiers() -> pd.DataFrame:
    return load("chantiers-a-paris-copie1", layer="perso")


def signalements() -> pd.DataFrame:
    return load("dans-ma-rue", layer="perso")


def parkings() -> pd.DataFrame:
    return load("stationnement-parking-public", layer="perso")


def voie_publique() -> pd.DataFrame:
    return load("stationnement-voie-publique-emplacements 1", layer="perso")
