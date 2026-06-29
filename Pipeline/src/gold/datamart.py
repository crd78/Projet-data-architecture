import glob
import math
import re
import sqlite3
import unicodedata
from pathlib import Path

import pandas as pd
import requests


PIPELINE_DIR = Path(__file__).resolve().parent.parent.parent
BASE_DIR = PIPELINE_DIR / "datasets_finaux"
KPI_IMPOSE_DIR = BASE_DIR / "KPI_impose_silver_enriched"
KPI_PERSONNALISE_DIR = BASE_DIR / "KPI_personnalise_silver_enriched"
GOLD_DIR = BASE_DIR / "gold"
DB_PATH = BASE_DIR / "paris_immobilier.db"
QUARTIERS_PATH = BASE_DIR / "KPI_impose_silver" / "quartiers_silver.parquet"

QUARTIER_COLS = [
    "arrondissement_quartier",
    "num_quartier",
    "nom_quartier",
    "surface_quartier",
    "geometry_quartier",
]


def _write_sql(table_name: str, df: pd.DataFrame) -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH, timeout=60) as conn:
        df.to_sql(table_name, conn, if_exists="replace", index=False)


def _normalize_text(value) -> str:
    if pd.isna(value):
        return ""
    text = unicodedata.normalize("NFD", str(value))
    text = text.encode("ascii", "ignore").decode("ascii")
    text = text.lower().strip()
    text = text.replace("_", " ")
    text = re.sub(r"[^\w\s]", " ", text)
    return re.sub(r"\s+", " ", text)


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


def _require_columns(df: pd.DataFrame, columns: list[str], source: Path) -> pd.DataFrame:
    missing = [col for col in columns if col not in df.columns]
    if missing:
        raise KeyError(f"Colonnes manquantes dans {source}: {missing}")
    return df[columns].copy()


def _filter_arrondissement(df: pd.DataFrame, column: str = "arrondissement") -> pd.DataFrame:
    df = df.copy()
    df[column] = pd.to_numeric(df[column], errors="coerce").astype("Int64")
    return df[df[column].between(1, 20)]


def _read_parquet(path: Path, columns: list[str] | None = None) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable: {path}")
    return pd.read_parquet(path, columns=columns)


def _with_api_quartier_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    replacements = {
        "arrondissement_quartier": "arrondissement",
        "surface_quartier": "surface",
        "geometry_quartier": "geometry",
    }
    for source, target in replacements.items():
        if source in df.columns:
            df[target] = df[source]
            df = df.drop(columns=[source])
    if "num_quartier" in df.columns:
        df["num_quartier"] = pd.to_numeric(df["num_quartier"], errors="coerce").astype("Int64")
    if "arrondissement" in df.columns:
        df["arrondissement"] = pd.to_numeric(df["arrondissement"], errors="coerce").astype("Int64")
    if "geometry" in df.columns:
        df["geometry"] = df["geometry"].astype("string")
    return df


def _drop_without_quartier(df: pd.DataFrame) -> pd.DataFrame:
    return df.dropna(subset=["num_quartier", "nom_quartier"]).copy()


def _score_sur_100(series: pd.Series, *, higher_is_better: bool = True) -> pd.Series:
    values = pd.to_numeric(series, errors="coerce").fillna(0).clip(lower=0)
    max_value = values.max()
    if pd.isna(max_value) or max_value <= 0:
        return pd.Series(0.0, index=series.index)

    max_log = math.log10(max_value + 1)
    normalized = values.map(lambda value: (math.log10(value + 1) / max_log) * 100)
    if not higher_is_better:
        normalized = 100 - normalized
    return normalized.round(2)


def _set_score_columns(
    df: pd.DataFrame,
    score_column: str,
    *,
    higher_is_better: bool = True,
    raw_digits: int = 6,
) -> pd.DataFrame:
    raw_values = pd.to_numeric(df[score_column], errors="coerce")
    normalized = _score_sur_100(raw_values, higher_is_better=higher_is_better)

    df[f"{score_column}_brut"] = raw_values.round(raw_digits)
    df[score_column] = normalized
    df[f"{score_column}_sur_100"] = normalized
    return df


def quartiers_paris():
    df = _read_parquet(QUARTIERS_PATH)
    result = _with_api_quartier_columns(df)
    _write_sql("quartiers_paris", result)


def activite_quartier():
    path = KPI_PERSONNALISE_DIR / "google_place.parquet"
    columns = [
        *QUARTIER_COLS,
        "gp_place_id",
        "gp_display_name",
        "gp_business_status",
        "gp_rating",
        "gp_user_rating_count",
    ]
    df = _clean_missing_values(_require_columns(_read_parquet(path), columns, path))
    df = _drop_without_quartier(df)
    df = df[df["gp_display_name"].notna() & df["gp_business_status"].notna()].copy()

    df["gp_rating"] = pd.to_numeric(df["gp_rating"], errors="coerce")
    df["gp_user_rating_count"] = pd.to_numeric(df["gp_user_rating_count"], errors="coerce").fillna(0)
    status = df["gp_business_status"].map(_normalize_text)

    df["open"] = (status == "operational").astype(int)
    df["closed_permanently"] = (status == "closed permanently").astype(int)
    df["closed_temporarily"] = (status == "closed temporarily").astype(int)
    df["close"] = df["closed_permanently"] + df["closed_temporarily"]

    result = df.groupby(QUARTIER_COLS, dropna=False).agg(
        gp_rating=("gp_rating", "mean"),
        gp_user_rating_count=("gp_user_rating_count", "sum"),
        gp_place_count=("gp_place_id", "nunique"),
        open=("open", "sum"),
        close=("close", "sum"),
        closed_permanently=("closed_permanently", "sum"),
        closed_temporarily=("closed_temporarily", "sum"),
    ).reset_index()

    result["gp_rating"] = result["gp_rating"].fillna(0)
    result["activite_quartier_score"] = (
        result["gp_place_count"] * 2
        + result["gp_rating"] * 10
        - result["close"] * 5
    )
    result = _set_score_columns(result, "activite_quartier_score", raw_digits=2)
    _write_sql("activite_quartier", _with_api_quartier_columns(result))


def nuisance_sonore():
    path = KPI_PERSONNALISE_DIR / "chantiers-a-paris-copie1-1.parquet"
    columns = [
        *QUARTIER_COLS,
        "reference_chantier",
        "date_debut_du_chantier",
        "date_fin_du_chantier",
        "surface_m2",
        "coef_nature_travaux",
        "coef_encombrant",
        "db_base",
        "taux_de_nuisance",
    ]
    df = _clean_missing_values(_require_columns(_read_parquet(path), columns, path))
    df = _drop_without_quartier(df)

    df["date_fin_du_chantier"] = pd.to_datetime(df["date_fin_du_chantier"], errors="coerce")
    df = df[df["date_fin_du_chantier"] >= pd.Timestamp.now()]

    for col in ["surface_m2", "db_base", "taux_de_nuisance", "coef_nature_travaux", "coef_encombrant"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["nuisance_sonore_score"] = (
        df["db_base"]
        * df["taux_de_nuisance"]
        * df["coef_nature_travaux"]
        * df["coef_encombrant"]
    )

    result = df.groupby(QUARTIER_COLS, dropna=False).agg(
        nb_chantiers=("reference_chantier", "nunique"),
        surface_chantiers_m2=("surface_m2", "sum"),
        nuisance_sonore_score=("nuisance_sonore_score", "sum"),
        date_fin_max=("date_fin_du_chantier", "max"),
    ).reset_index()
    result = _set_score_columns(result, "nuisance_sonore_score", raw_digits=2)

    _write_sql("nuisance_sonore", _with_api_quartier_columns(result))


def indice_trafic_quartier() -> pd.DataFrame:
    frames = []
    offset = 0

    while True:
        url = (
            "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/"
            "comptages-routiers-permanents/records?"
            "select=libelle,etat_trafic,count(libelle)"
            "&where=etat_trafic!='Inconnu'"
            "&group_by=libelle,etat_trafic,geo_cluster(geo_point_2d,1)"
            "&limit=100"
            f"&offset={offset}"
        )

        try:
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            data = response.json().get("results", [])
        except (requests.RequestException, ValueError):
            return pd.DataFrame()

        if not data:
            break

        frame = pd.DataFrame(data)
        if "libelle" not in frame.columns:
            break

        frame["libelle"] = frame["libelle"].astype("string").str.replace("_", " ", regex=False)
        frames.append(frame)
        offset += 100

    if not frames:
        return pd.DataFrame()

    df = pd.concat(frames, ignore_index=True)
    count_col = next((col for col in df.columns if col.startswith("count")), None)
    if count_col is None:
        df["traffic_count"] = 1
        count_col = "traffic_count"

    return df.loc[df.groupby("libelle")[count_col].idxmax()].reset_index(drop=True)


def disponibilite_stationnement():
    park_path = KPI_PERSONNALISE_DIR / "stationnement-parking-public.parquet"
    voirie_path = KPI_PERSONNALISE_DIR / "stationnement-voie-publique-emplacements.parquet"

    park_cols = [*QUARTIER_COLS, "nbre_total_places", "nbre_place_voit_elec"]
    voirie_cols = [*QUARTIER_COLS, "nombre_places_reelles"]

    df_park = _drop_without_quartier(_require_columns(_read_parquet(park_path), park_cols, park_path))
    df_voirie = _drop_without_quartier(_require_columns(_read_parquet(voirie_path), voirie_cols, voirie_path))

    df_park["nbre_total_places"] = pd.to_numeric(df_park["nbre_total_places"], errors="coerce").fillna(0)
    df_park["nbre_place_voit_elec"] = pd.to_numeric(df_park["nbre_place_voit_elec"], errors="coerce").fillna(0)
    df_voirie["nombre_places_reelles"] = pd.to_numeric(df_voirie["nombre_places_reelles"], errors="coerce").fillna(0)

    df_park_agg = df_park.groupby(QUARTIER_COLS, dropna=False).agg(
        nombre_places_parking_public=("nbre_total_places", "sum"),
        nombre_places_voiture_electrique=("nbre_place_voit_elec", "sum"),
    ).reset_index()

    df_voirie_agg = df_voirie.groupby(QUARTIER_COLS, dropna=False).agg(
        nombre_places_voirie=("nombre_places_reelles", "sum")
    ).reset_index()

    result = df_park_agg.merge(df_voirie_agg, on=QUARTIER_COLS, how="outer")
    for col in ["nombre_places_parking_public", "nombre_places_voiture_electrique", "nombre_places_voirie"]:
        result[col] = pd.to_numeric(result[col], errors="coerce").fillna(0)

    result["disponibilite_stationnement_score"] = (
        result["nombre_places_voirie"] * 0.6
        + result["nombre_places_parking_public"] * 0.4
    )
    result = _set_score_columns(result, "disponibilite_stationnement_score", raw_digits=2)

    _write_sql("disponibilite_stationnement", _with_api_quartier_columns(result))


DECLARATION_CODES = {
    "proprete": "proprete",
    "graffitis tags affiches et autocollants": "graffitis",
    "mobiliers urbains": "mobiliers_urbains",
    "degradation du sol": "degradation_sol",
    "objets abandonnes": "objets_abandonnes",
}

DECLARATION_WEIGHTS = {
    "proprete": 1.0,
    "graffitis": 0.7,
    "mobiliers_urbains": 0.9,
    "degradation_sol": 1.2,
    "objets_abandonnes": 1.1,
}


def proprete_general():
    path = KPI_PERSONNALISE_DIR / "dans-ma-rue.parquet"
    columns = [*QUARTIER_COLS, "type_declaration"]
    df = _clean_missing_values(_require_columns(_read_parquet(path), columns, path))
    df = _drop_without_quartier(df)

    df["type_code"] = df["type_declaration"].map(
        lambda value: DECLARATION_CODES.get(_normalize_text(value))
    )
    df = df[df["type_code"].notna()]

    if df.empty:
        _write_sql("proprete_general", pd.DataFrame())
        return

    counts = df.groupby(QUARTIER_COLS + ["type_code"], dropna=False).size().unstack(fill_value=0).reset_index()
    for code in DECLARATION_WEIGHTS:
        if code not in counts.columns:
            counts[code] = 0

    counts["somme_poids_type"] = sum(
        counts[code] * weight for code, weight in DECLARATION_WEIGHTS.items()
    )
    counts["proprete_score"] = counts["somme_poids_type"] / pd.to_numeric(
        counts["surface_quartier"], errors="coerce"
    ).replace(0, pd.NA)
    counts = _set_score_columns(
        counts,
        "proprete_score",
        higher_is_better=False,
        raw_digits=6,
    )

    counts = counts.rename(
        columns={
            "proprete": "decl_proprete",
            "graffitis": "decl_graffitis_tags_affiches_autocollants",
            "mobiliers_urbains": "decl_mobiliers_urbains",
            "degradation_sol": "decl_degradation_du_sol",
            "objets_abandonnes": "decl_objets_abandonnes",
        }
    )

    _write_sql("proprete_general", _with_api_quartier_columns(counts))


def logement_sociaux():
    path = KPI_IMPOSE_DIR / "logements-sociaux-finances-a-paris.parquet"
    df = _read_parquet(path)
    df = df.drop(columns=["coordonnee_en_x_l93", "coordonnee_en_y_l93", "geo_shape"], errors="ignore")
    _write_sql("logement_sociaux", _with_api_quartier_columns(df))


def location_arrondissement():
    path = KPI_IMPOSE_DIR / "logement-encadrement-des-loyers.parquet"
    df = _read_parquet(path)
    df = df.drop(columns=["numero_insee_du_quartier", "geo_shape"], errors="ignore")
    _write_sql("location_arrondissement", _with_api_quartier_columns(df))


def somme_prix_paris_par_annee():
    path = KPI_PERSONNALISE_DIR / "Somme_Prix_Paris_Par_Annee_2019_2024.parquet"
    df = _read_parquet(path)

    if "annee" in df.columns:
        df["annee"] = pd.to_numeric(df["annee"], errors="coerce").astype("Int64")

    numeric_columns = ["1er", *[f"{arrondissement}e" for arrondissement in range(2, 21)]]
    numeric_columns += ["somme_paris_annuelle", "moyenne_paris_annuelle"]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "annee" in df.columns:
        df = df.sort_values("annee").reset_index(drop=True)

    _write_sql("somme_prix_paris_par_annee", df)


def _normalize_iris(series: pd.Series) -> pd.Series:
    return series.astype("string").str.replace(r"\.0$", "", regex=True)


def population_niveau_vie():
    habitant_path = KPI_IMPOSE_DIR / "base-ic-evol-struct-pop-2021.parquet"
    df_nb_habitant = _require_columns(
        _read_parquet(habitant_path),
        ["iris", "p21_pop"],
        habitant_path,
    )
    df_nb_habitant["iris"] = _normalize_iris(df_nb_habitant["iris"])
    df_nb_habitant = df_nb_habitant[df_nb_habitant["iris"].str.startswith("75", na=False)]

    files = sorted(glob.glob(str(KPI_IMPOSE_DIR / "BASE_TD_FILO*.parquet")))
    if not files:
        raise FileNotFoundError(f"Aucun fichier trouve avec le pattern: {KPI_IMPOSE_DIR / 'BASE_TD_FILO*.parquet'}")

    frames = []
    for file_path in files:
        df = _read_parquet(Path(file_path))
        df.columns = df.columns.str.lower()

        col_iris = next((col for col in df.columns if re.fullmatch(r"iris", col)), None)
        col_dec_med = next((col for col in df.columns if re.match(r"dec_med\d*", col)), None)
        col_dec_pimp = next((col for col in df.columns if re.match(r"dec_pimp\d*", col)), None)

        if not all([col_iris, col_dec_med, col_dec_pimp]):
            continue

        df = df[[col_iris, col_dec_med, col_dec_pimp]].rename(
            columns={
                col_iris: "iris",
                col_dec_med: "dec_med",
                col_dec_pimp: "dec_pimp",
            }
        )
        parts = Path(file_path).stem.split("_")
        year = next((p for p in parts if re.fullmatch(r"\d{4}", p)), None)
        df["annee"] = year
        df["iris"] = _normalize_iris(df["iris"])
        frames.append(df[df["iris"].str.startswith("75", na=False)])

    if not frames:
        raise ValueError("Aucun fichier BASE_TD_FILO valide n'a pu etre traite.")

    result = pd.concat(frames, ignore_index=True)
    result = result.merge(df_nb_habitant, on="iris", how="left")
    _write_sql("population_niveau_vie", result)


def prix_arrondissement():
    path = KPI_IMPOSE_DIR / "stats_whole_period.parquet"
    df = _read_parquet(path)
    df["code_geo"] = df["code_geo"].astype("string")
    df = df[(df["code_geo"].str.startswith("751", na=False)) & (df["echelle_geo"] == "commune")]
    _write_sql("prix_arrondissement", df)


if __name__ == "__main__":
    prix_arrondissement()
