import glob
import re
import sqlite3
import unicodedata
from pathlib import Path

import pandas as pd
import requests

try:
    from .func import point_dans_zone
except ImportError:
    from func import point_dans_zone


PIPELINE_DIR = Path(__file__).resolve().parent.parent.parent
BASE_DIR = PIPELINE_DIR / "datasets_finaux"
KPI_IMPOSE_DIR = BASE_DIR / "KPI_impose_silver"
KPI_PERSONNALISE_DIR = BASE_DIR / "KPI_personnalise_silver"
GOLD_DIR = BASE_DIR / "gold"
DB_PATH = BASE_DIR / "paris_immobilier.db"
QUARTIERS_PATH = KPI_IMPOSE_DIR / "quartier_paris.parquet"


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


def _quartier_name_by_code() -> pd.Series:
    df_quartiers = pd.read_parquet(QUARTIERS_PATH, columns=["c_qu", "l_qu"])
    return df_quartiers.drop_duplicates("c_qu").set_index("c_qu")["l_qu"]


def _point_lookup(row, include_surface: bool = False):
    arr = row.get("arrondissement")
    if pd.isna(arr):
        arr = None

    return point_dans_zone(
        row.get("latitude"),
        row.get("longitude"),
        QUARTIERS_PATH,
        arr,
        other_column="surface" if include_surface else None,
    )


def _assign_quartier(df: pd.DataFrame, include_surface: bool = False) -> pd.DataFrame:
    df = df.copy()
    target_cols = ["num_quartier", "nom_quartier"]
    if include_surface:
        target_cols.append("surface")

    if df.empty:
        for col in target_cols:
            df[col] = pd.Series(dtype="object")
        return df

    df[target_cols] = df.apply(
        lambda row: _point_lookup(row, include_surface=include_surface),
        axis=1,
        result_type="expand",
    )
    return df


def quartiers_paris():
    df = pd.read_parquet(QUARTIERS_PATH)
    _write_sql("quartiers_paris", df)


def _read_places_source() -> pd.DataFrame:
    required = [
        "arro",
        "qua",
        "gp_place_id",
        "gp_display_name",
        "gp_business_status",
        "gp_rating",
        "gp_user_rating_count",
    ]
    candidates = [
        KPI_PERSONNALISE_DIR / "google_place.parquet",
        KPI_PERSONNALISE_DIR / "BDCOM_2023.parquet",
    ]

    for path in candidates:
        if not path.exists():
            continue
        df = pd.read_parquet(path)
        if all(col in df.columns for col in required):
            return df[required].copy()

    bdc_path = KPI_PERSONNALISE_DIR / "BDCOM_2023.parquet"
    google_path = KPI_PERSONNALISE_DIR / "google_place.parquet"
    if bdc_path.exists() and google_path.exists():
        bdc = pd.read_parquet(bdc_path)
        google = pd.read_parquet(google_path)
        keys = [key for key in ["arro", "qua", "num", "codact"] if key in bdc.columns and key in google.columns]
        if keys and all(col in google.columns for col in required[2:]):
            google = google[keys + required[2:]].drop_duplicates()
            merged = bdc.merge(google, on=keys, how="left")
            return _require_columns(merged, required, bdc_path)

    raise FileNotFoundError("Aucune source avec les colonnes Google Places attendues.")


def activite_quartier():
    df = _clean_missing_values(_read_places_source())
    df = df[df["gp_display_name"].notna() & df["gp_business_status"].notna()].copy()

    df["gp_rating"] = pd.to_numeric(df["gp_rating"], errors="coerce")
    df["gp_user_rating_count"] = pd.to_numeric(df["gp_user_rating_count"], errors="coerce").fillna(0)
    status = df["gp_business_status"].map(_normalize_text)

    df["open"] = (status == "operational").astype(int)
    df["closed_permanently"] = (status == "closed permanently").astype(int)
    df["closed_temporarily"] = (status == "closed temporarily").astype(int)
    df["close"] = df["closed_permanently"] + df["closed_temporarily"]
    df["nom_quartier"] = df["qua"].map(_quartier_name_by_code())

    result = df.groupby(["nom_quartier", "qua", "arro"], dropna=False).agg(
        gp_rating=("gp_rating", "mean"),
        gp_user_rating_count=("gp_user_rating_count", "sum"),
        gp_place_id=("gp_place_id", "nunique"),
        open=("open", "sum"),
        close=("close", "sum"),
        closed_permanently=("closed_permanently", "sum"),
        closed_temporarily=("closed_temporarily", "sum"),
    ).reset_index()

    result["gp_rating"] = result["gp_rating"].fillna(0)
    result["activite_quartier_score"] = (
        result["gp_place_id"] * 2
        + result["gp_rating"] * 10
        - result["close"] * 5
    )
    _write_sql("activite_quartier", result)


def nuisance_sonore():
    path = KPI_PERSONNALISE_DIR / "chantiers-a-paris-copie1-1.parquet"
    columns = [
        "code_postal_arrondissement_commune",
        "date_debut_du_chantier",
        "date_fin_du_chantier",
        "surface_m2",
        "synthese_nature_du_chantier",
        "encombrement_espace_public",
        "impact_stationnement",
        "geo_shape",
        "coef_nature_travaux",
        "coef_encombrant",
        "db_base",
        "taux_de_nuisance",
        "latitude",
        "longitude",
    ]
    df = _require_columns(pd.read_parquet(path), columns, path)

    df["date_fin_du_chantier"] = pd.to_datetime(df["date_fin_du_chantier"], errors="coerce")
    df = df[df["date_fin_du_chantier"].notna()]
    df = df[df["date_fin_du_chantier"] >= pd.Timestamp.now()]

    for col in ["db_base", "taux_de_nuisance", "coef_nature_travaux", "coef_encombrant"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["nuisance_sonore_score"] = (
        df["db_base"]
        * df["taux_de_nuisance"]
        * df["coef_nature_travaux"]
        * df["coef_encombrant"]
    )
    _write_sql("nuisance_sonore", df)


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


def _traffic_index(label) -> int:
    normalized = _normalize_text(label)
    if normalized == "fluide":
        return 1
    if "sature" in normalized:
        return 3
    return 2


def _traffic_by_quartier() -> pd.DataFrame:
    df_trafic = indice_trafic_quartier()
    if df_trafic.empty or "geo_cluster(geo_point_2d,1)" not in df_trafic.columns:
        return pd.DataFrame(columns=["num_quartier", "nom_quartier", "indice_trafic_quartier"])

    def extract_lat_lon(cluster):
        if not isinstance(cluster, dict):
            return pd.Series({"latitude": pd.NA, "longitude": pd.NA})
        centroid = cluster.get("cluster_centroid") or {}
        return pd.Series({"latitude": centroid.get("lat"), "longitude": centroid.get("lon")})

    df_trafic[["latitude", "longitude"]] = df_trafic["geo_cluster(geo_point_2d,1)"].apply(extract_lat_lon)
    df_trafic = _assign_quartier(df_trafic)
    df_trafic["indice_trafic_quartier"] = df_trafic["etat_trafic"].map(_traffic_index)
    df_trafic = df_trafic.dropna(subset=["num_quartier", "nom_quartier"])

    return df_trafic.groupby(["num_quartier", "nom_quartier"], as_index=False).agg(
        indice_trafic_quartier=("indice_trafic_quartier", "max")
    )


def disponibilite_stationnement():
    park_path = KPI_PERSONNALISE_DIR / "stationnement-parking-public.parquet"
    voirie_path = KPI_PERSONNALISE_DIR / "stationnement-voie-publique-emplacements.parquet"

    park_cols = [
        "nom_parc",
        "adresse_principale",
        "nbre_total_places",
        "nbre_place_voit_elec",
        "adresses_entrees",
        "arrondissement",
        "latitude",
        "longitude",
    ]
    voirie_cols = [
        "regime_prioritaire",
        "regime_particulier",
        "arrondissement",
        "nombre_places_reelles",
        "zones_residentielles",
        "numero_voie",
        "type_voie",
        "nom_voie",
        "latitude",
        "longitude",
    ]

    df_park = _filter_arrondissement(_require_columns(pd.read_parquet(park_path), park_cols, park_path))
    df_voirie = _filter_arrondissement(_require_columns(pd.read_parquet(voirie_path), voirie_cols, voirie_path))

    df_park["nbre_total_places"] = pd.to_numeric(df_park["nbre_total_places"], errors="coerce").fillna(0)
    df_voirie["nombre_places_reelles"] = pd.to_numeric(df_voirie["nombre_places_reelles"], errors="coerce").fillna(0)

    df_park = _assign_quartier(df_park).dropna(subset=["num_quartier", "nom_quartier"])
    df_voirie = _assign_quartier(df_voirie).dropna(subset=["num_quartier", "nom_quartier"])

    df_park = df_park.groupby(["arrondissement", "num_quartier", "nom_quartier"], as_index=False).agg(
        nombre_places_parking_public=("nbre_total_places", "sum")
    )
    df_voirie = df_voirie.groupby(["arrondissement", "num_quartier", "nom_quartier"], as_index=False).agg(
        nombre_places_voirie=("nombre_places_reelles", "sum")
    )

    df = df_park.merge(
        df_voirie,
        on=["arrondissement", "num_quartier", "nom_quartier"],
        how="outer",
    )
    df[["nombre_places_parking_public", "nombre_places_voirie"]] = df[
        ["nombre_places_parking_public", "nombre_places_voirie"]
    ].fillna(0)

    trafic = _traffic_by_quartier()
    df = df.merge(trafic, on=["num_quartier", "nom_quartier"], how="left")
    df["indice_trafic_quartier"] = df["indice_trafic_quartier"].fillna(1)
    df["disponibilite_stationnement_score"] = (
        df["nombre_places_voirie"] * 0.6
        + df["nombre_places_parking_public"] * 0.4
    ) / df["indice_trafic_quartier"]

    _write_sql("disponibilite_stationnement", df)


DECLARATION_CODES = {
    "proprete": "proprete",
    "graffitis tags affiches et autocollants": "graffitis",
    "mobiliers urbains": "mobiliers_urbains",
    "degradation du sol": "degradation_sol",
}

DECLARATION_WEIGHTS = {
    "proprete": 1.0,
    "graffitis": 0.7,
    "mobiliers_urbains": 0.9,
    "degradation_sol": 1.2,
}


def proprete_general():
    path = KPI_PERSONNALISE_DIR / "dans-ma-rue.parquet"
    df = pd.read_parquet(path)
    required = ["type_declaration", "arrondissement", "latitude", "longitude"]
    _require_columns(df, required, path)

    df = df.copy()
    df["type_code"] = df["type_declaration"].map(lambda value: DECLARATION_CODES.get(_normalize_text(value)))
    df = df[df["type_code"].notna()]
    df = _filter_arrondissement(df)

    if df.empty:
        _write_sql("proprete_general", pd.DataFrame())
        return

    df = _assign_quartier(df, include_surface=True)
    df = df.dropna(subset=["num_quartier", "nom_quartier", "surface"])
    df["surface"] = pd.to_numeric(df["surface"], errors="coerce")
    df = df[df["surface"].notna() & (df["surface"] > 0)]

    group_cols = ["arrondissement", "num_quartier", "nom_quartier", "surface"]
    counts = df.groupby(group_cols + ["type_code"]).size().unstack(fill_value=0).reset_index()
    for code in DECLARATION_WEIGHTS:
        if code not in counts.columns:
            counts[code] = 0

    counts["somme_poids_type"] = sum(
        counts[code] * weight for code, weight in DECLARATION_WEIGHTS.items()
    )
    counts["proprete_score"] = counts["somme_poids_type"] / counts["surface"]
    counts = counts.rename(
        columns={
            "proprete": "decl_proprete",
            "graffitis": "decl_graffitis_tags_affiches_autocollants",
            "mobiliers_urbains": "decl_mobiliers_urbains",
            "degradation_sol": "decl_degradation_du_sol",
        }
    )

    _write_sql("proprete_general", counts)


def logement_sociaux():
    path = KPI_IMPOSE_DIR / "logements-sociaux-finances-a-paris.parquet"
    df = pd.read_parquet(path)
    df = df.drop(columns=["coordonnee_en_x_l93", "coordonnee_en_y_l93", "geo_shape"], errors="ignore")
    _write_sql("logement_sociaux", df)


def location_arrondissement():
    path = KPI_IMPOSE_DIR / "logement-encadrement-des-loyers.parquet"
    df = pd.read_parquet(path)
    df = df.drop(columns=["numero_insee_du_quartier", "geo_shape"], errors="ignore")
    _write_sql("location_arrondissement", df)


def somme_prix_paris_par_annee():
    path = KPI_PERSONNALISE_DIR / "Somme_Prix_Paris_Par_Annee_2019_2024.parquet"
    df = pd.read_parquet(path)

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
        pd.read_parquet(habitant_path),
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
        df = pd.read_parquet(file_path)
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
        parts = file_path.split(".")[0]
        parts = parts.split("_")
        year = next((p for p in parts if re.fullmatch(r"\d{4}", p)), None)
        df["année"] = year
        df["iris"] = _normalize_iris(df["iris"])
        frames.append(df[df["iris"].str.startswith("75", na=False)])

    if not frames:
        raise ValueError("Aucun fichier BASE_TD_FILO valide n'a pu etre traite.")

    result = pd.concat(frames, ignore_index=True)
    result = result.merge(df_nb_habitant, on="iris", how="left")
    _write_sql("population_niveau_vie", result)


def prix_arrondissement():
    path = KPI_IMPOSE_DIR / "stats_whole_period.parquet"
    df = pd.read_parquet(path)
    df["code_geo"] = df["code_geo"].astype("string")
    df = df[(df["code_geo"].str.startswith("751", na=False)) & (df["echelle_geo"] == "commune")]
    _write_sql("prix_arrondissement", df)


if __name__ == "__main__":
    prix_arrondissement()
