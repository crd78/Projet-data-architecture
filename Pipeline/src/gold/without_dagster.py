import os
import sqlite3
import pandas as pd
from pathlib import Path
from func import point_dans_zone
import requests as r
import json


# 📁 Dossier contenant les fichiers parquet
PIPELINE_DIR = Path(__file__).resolve().parent.parent.parent
BASE_DIR     = PIPELINE_DIR / "datasets_finaux"

parquet_folder = "KPI_personnalise_silver"

# Base SQLite
db_path = "paris_immobilier.db"

# Connexion à la base
conn = sqlite3.connect(db_path)

# Table de tous les quartiers
def quartiers_paris():
    file = "quartier_paris.parquet"
    file_path = os.path.join(f"{BASE_DIR}/KPI_impose_silver", file)
    df = pd.read_parquet(file_path)

    #  Connexion SQLite
    conn = sqlite3.connect(db_path)

    #  Création + insertion
    df.to_sql("quartiers_paris", conn, if_exists="replace", index=False)

# Score nuisance sonore
def activite_quartier():
    quartiers_paris_file = "quartier_paris.parquet"
    quartiers_paris_file_path = os.path.join(f"{BASE_DIR}/KPI_impose_silver", quartiers_paris_file)
    df_quartiers = pd.read_parquet(quartiers_paris_file_path)

    colonnes = [
        "arro", "qua", "num",
        "typ_voie", "lib_voie", "codact", "ens",
        "gp_place_id", "gp_display_name",
        "gp_business_status", "gp_rating",
        "gp_user_rating_count"
    ]
    file = "BDCOM_2023.parquet"
    file_path = os.path.join(f"{BASE_DIR}/{parquet_folder}", file)
    df = pd.read_parquet(file_path)

    print(len(df_quartiers), "len quartiers")

    df = df[colonnes]
    df = df[df["gp_display_name"].isna() == False]
    df["nom_quartier"] = df.apply(
        lambda row: (
            df_quartiers["l_qu"][df_quartiers["c_qu"] == row["qua"]].iloc[0]
            if not df_quartiers["l_qu"][df_quartiers["c_qu"] == row["qua"]].empty
            else None
        ), axis=1)
    
    df = df[df["gp_business_status"].isna() == False]
    df_dummies = pd.get_dummies(df["gp_business_status"])
    df = pd.concat([df, df_dummies], axis=1)

    df["close"] = df["CLOSED_PERMANENTLY"] + df["CLOSED_TEMPORARILY"]
    
    df.rename(columns={"OPERATIONAL": "open"}, inplace=True)
    
    df = df.groupby(["nom_quartier", "qua", "arro"]).agg({
        "gp_rating": "mean",
        "gp_user_rating_count": "sum",
        "gp_place_id": "count",
        "open": "sum",
        "close": "sum",
        "CLOSED_PERMANENTLY": "sum",
        "CLOSED_TEMPORARILY": "sum"
    }).reset_index()

    df["activite_quartier_score"] = (df["gp_place_id"] * 2 ) + ((df["gp_rating"] * 10) - (df["close"] * 5))
    # df["activite_quartier_score"] = (df["gp_place_id"]) + ((df["gp_rating"] * 15) - (df["close"] * 3))
    

    conn = sqlite3.connect(db_path)
    df.to_sql("activite_quartier", conn, if_exists="replace", index=False)

def nuisance_sonore():
    file = "chantiers-a-paris-copie1-1.parquet"
    file_path = os.path.join(f"{BASE_DIR}/KPI_personnalise_silver", file)
    df = pd.read_parquet(file_path)

    colonnes = ["code_postal_arrondissement_commune", "date_debut_du_chantier",
                "date_fin_du_chantier", "surface_m2", "synthese_nature_du_chantier",
                "encombrement_espace_public", "impact_stationnement", 'geo_shape', "coef_nature_travaux", "coef_encombrant", "db_base", "taux_de_nuisance", "latitude", "longitude"]
    df = df[colonnes]

    df = df[df["date_fin_du_chantier"] >= pd.Timestamp.now()]
    df["nuisance_sonore_score"] = df["db_base"] * df["taux_de_nuisance"] * df["coef_nature_travaux"] * df["coef_encombrant"]



    conn = sqlite3.connect(db_path)
    df.to_sql("nuisance_sonore", conn, if_exists="replace", index=False)



#Formule: (Places_Voirie x 0.6) + (Places_Parking_Public x 0.4)/Indice du trafic du quartier


def indice_trafic_quartier():
    traf = []
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

        response = r.get(url)
        data = response.json().get("results", [])

        if not data:
            break

        df = pd.DataFrame(data)

        if "libelle" not in df.columns:
            break

        df["libelle"] = df["libelle"].str.replace("_", " ")

        traf.append(df)

        offset += 100

    df = pd.concat(traf, ignore_index=True)

    result = df.loc[
        df.groupby("libelle")["count(libelle)"].idxmax()
    ].reset_index(drop=True)

    print(result["etat_trafic"].unique(), "états de trafic uniques")

    return result



def disponibilite_stationnement():
    park_public_file = "stationnement-parking-public.parquet"
    stationnement_voirie_file = "stationnement-voie-publique-emplacements.parquet"

    park_public_file_path = os.path.join(f"{BASE_DIR}/KPI_personnalise_silver", park_public_file)
    stationnement_voirie_file_path = os.path.join(f"{BASE_DIR}/KPI_personnalise_silver", stationnement_voirie_file)

    df_park_public = pd.read_parquet(park_public_file_path)
    df_stationnement_voirie = pd.read_parquet(stationnement_voirie_file_path)

    colonnes_park_public = ["nom_parc", "adresse_principale", "nbre_total_places", "nbre_place_voit_elec", "adresses_entrees", "arrondissement", "latitude", "longitude"]
    colonnes_stationnement_voirie = ["regime_prioritaire", "regime_particulier", "arrondissement", "nombre_places_reelles", "zones_residentielles", "numero_voie", "type_voie", "nom_voie", "latitude", "longitude"]

    df_park_public = df_park_public[colonnes_park_public]
    df_park_public["is_parking"] = 1

    df_park_public = df_park_public[df_park_public["arrondissement"] <= 20]
    df_park_public["is_parking"] = df_park_public["is_parking"].fillna(0)

    df_stationnement_voirie = df_stationnement_voirie[colonnes_stationnement_voirie]
    df_stationnement_voirie["is_voirie"] = 1

    df_stationnement_voirie = df_stationnement_voirie[df_stationnement_voirie["arrondissement"] <= 20]
    df_stationnement_voirie["is_voirie"] = df_stationnement_voirie["is_voirie"].fillna(0)


    df_park_public[["num_quartier", "nom_quartier"]] = df_park_public.apply(
        lambda row: point_dans_zone(
            row["latitude"],
            row["longitude"],
            f"{BASE_DIR}/KPI_impose_silver/quartier_paris.parquet",
            row["arrondissement"]
        ),
        axis=1,
        result_type="expand"
    )
    df_park_public = df_park_public.groupby(["arrondissement", "num_quartier", "nom_quartier"]).agg({
        "nbre_total_places": "sum",
        "is_parking": "mean"
    }).reset_index()
    df_park_public.to_csv("df_park_public.csv", index=False)

    df_stationnement_voirie[["num_quartier", "nom_quartier"]] = df_stationnement_voirie.apply(
        lambda row: point_dans_zone(
            row["latitude"],
            row["longitude"],
            f"{BASE_DIR}/KPI_impose_silver/quartier_paris.parquet",
            row["arrondissement"]
        ),
        axis=1,
        result_type="expand"
    )
    df_stationnement_voirie = df_stationnement_voirie.groupby(["arrondissement", "num_quartier", "nom_quartier"]).agg({
        "nombre_places_reelles": "sum",
        "is_voirie": "mean"
    }).reset_index()
    df_stationnement_voirie.to_csv("df_stationnement_voirie.csv", index=False)

    df = pd.merge(df_park_public, df_stationnement_voirie, on=["arrondissement", "num_quartier", "nom_quartier"], how="outer")
    df["is_voirie"] = df["is_voirie"].fillna(0)
    df["is_parking"] = df["is_parking"].fillna(0)
    df.to_csv("df_stationnement_combine.csv", index=False)
    
    df_trafic = indice_trafic_quartier()
    df_trafic[["num_quartier", "nom_quartier"]] = df_trafic.apply(
        lambda row: point_dans_zone(
            row["geo_cluster(geo_point_2d,1)"]["cluster_centroid"]["lat"],
            row["geo_cluster(geo_point_2d,1)"]["cluster_centroid"]["lon"],
            f"{BASE_DIR}/KPI_impose_silver/quartier_paris.parquet",
        ),
        axis=1,
        result_type="expand"
    )  

    TRAFIC_INDEX = {
        "Fluide": 1,      # trafic fluide = conditions optimales
        "Saturé": 3,      # trafic saturé = conditions dégradées
        "Inconnu": 2      # valeur neutre par défaut
    }

    df_trafic.to_csv("df_trafic.csv", index=False)
    df = df.merge(df_trafic, left_on=["num_quartier", "nom_quartier"], right_on=["num_quartier", "nom_quartier"], how="left")
    print(len(df), "len df après merge trafic")
    df["indice_trafic_quartier"] = df["etat_trafic"].map(TRAFIC_INDEX)


    print(len(df.arrondissement.unique()))
    df = df.groupby(["arrondissement", "num_quartier", "nom_quartier"]).agg({
        "indice_trafic_quartier": "first",
        "nbre_total_places": "sum",
        "nombre_places_reelles": "sum"
    }).reset_index()
    print(len(df), "len df après groupby final")
    df.rename(columns={
        "nbre_total_places": "nombre_places_parking_public",
        "nombre_places_reelles": "nombre_places_voirie"
    }, inplace=True)

    df["indice_trafic_quartier"] = df["indice_trafic_quartier"].fillna(1)  # Valeur neutre pour les quartiers sans données de trafic

    df["disponibilite_stationnement_score"] = ((df["nombre_places_voirie"] * 0.6) + (df["nombre_places_parking_public"] * 0.4)) / df["indice_trafic_quartier"]
    df.to_csv("df_stationnement_combine_score.csv", index=False)
    conn = sqlite3.connect(db_path)
    df.to_sql("disponibilite_stationnement", conn, if_exists="replace", index=False)

def proprete_general():
    file = "dans-ma-rue.parquet"
    file_path = os.path.join(f"{BASE_DIR}/KPI_personnalise_silver", file)
    df = pd.read_parquet(file_path)

    salete = ["Propreté", "Graffitis, tags, affiches et autocollants", "Mobiliers urbains", "Dégradation du sol"]
    df = df[df["type_declaration"].isin(salete)]

    DECLARATION_INDEX = {
        "Propreté": 1,
        "Graffitis, tags, affiches et autocollants": 0.7,
        "Mobiliers urbains": 0.9,
        "Dégradation du sol": 1.2
    }

    df = df[df["arrondissement"] <= 20]

    df[["num_quartier", "nom_quartier", "surface"]] = df.apply(
        lambda row: point_dans_zone(
            row["latitude"],
            row["longitude"],
            f"{BASE_DIR}/KPI_impose_silver/quartier_paris.parquet",
            row["arrondissement"],
            other_column="surface"
        ),
        axis=1,
        result_type="expand"
    )

    df = pd.get_dummies(df, columns=["type_declaration"], prefix="decl")

    df = df.groupby(["arrondissement", "num_quartier", "nom_quartier", "surface"]).agg({
        "decl_Propreté": "sum",
        "decl_Graffitis, tags, affiches et autocollants": "sum",
        "decl_Mobiliers urbains": "sum",
        "decl_Dégradation du sol": "sum"
    }).reset_index()

    print(df.head())

    df["somme_poids_type"] = df["decl_Propreté"] + df["decl_Graffitis, tags, affiches et autocollants"] * 0.7 + df["decl_Mobiliers urbains"] * 0.9 + df["decl_Dégradation du sol"] * 1.2
    df["proprete_score"] = df["somme_poids_type"] / df["surface"]
    
    conn = sqlite3.connect(db_path)
    df.to_sql("proprete_general", conn, if_exists="replace", index=False)


def logement_sociaux():
    file = "logements-sociaux-finances-a-paris.parquet"
    file_path = os.path.join(f"{BASE_DIR}/KPI_impose_silver", file)
    
    logement_sociaux = pd.read_parquet(file_path)
    logement_sociaux_col = ["coordonnee_en_x_l93", "coordonnee_en_y_l93", "geo_shape"]
    logement_sociaux.drop(columns=logement_sociaux_col, inplace=True)
    conn = sqlite3.connect(db_path)
    logement_sociaux.to_sql("logement_sociaux", conn, if_exists="replace", index=False)

def location_arrondissement():
    file = "logement-encadrement-des-loyers.parquet"
    file_path = os.path.join(f"{BASE_DIR}/KPI_impose_silver", file)
    
    location_arrondissement = pd.read_parquet(file_path)
    location_arrondissement_col = ["numero_insee_du_quartier", "geo_shape"]
    location_arrondissement.drop(columns=location_arrondissement_col, inplace=True)

    conn = sqlite3.connect(db_path)
    location_arrondissement.to_sql("location_arrondissement", conn, if_exists="replace", index=False)

import os
import re
import sqlite3
import pandas as pd
import glob

def population_niveau_vie():
    """
    Charge tous les fichiers Parquet commençant par 'BASE_TD_FILO',
    détecte dynamiquement les colonnes pertinentes (iris, libcom, dec_med*, dec_pimp*),
    filtre sur Paris, et insère dans SQLite.
    """
    file = "base-ic-evol-struct-pop-2021.parquet"
    file_path = os.path.join(f"{BASE_DIR}/KPI_impose_silver", file)
    df_nb_habitant = pd.read_parquet(file_path)
    df_nb_habitant_col = ["iris", "p21_pop"]
    
    df_nb_habitant = df_nb_habitant[df_nb_habitant_col]
    df_nb_habitant = df_nb_habitant[(df_nb_habitant["iris"] >= 750000000)	& (df_nb_habitant["iris"] < 760000000)]



    # 1. Récupération automatique de tous les fichiers correspondants
    pattern = os.path.join(BASE_DIR, "KPI_impose_silver", "BASE_TD_FILO*.parquet")
    files = glob.glob(pattern)

    if not files:
        raise FileNotFoundError(f"Aucun fichier trouvé avec le pattern : {pattern}")

    dfs = []

    print(files)

    for file_path in files:
        df = pd.read_parquet(file_path)

        # Normaliser les noms de colonnes en minuscules pour la recherche
        df.columns = df.columns.str.lower()

        # 2. Détection dynamique des colonnes — indépendante du suffixe d'année
        col_iris    = next((c for c in df.columns if re.fullmatch(r'iris',    c)), None)
        col_dec_med = next((c for c in df.columns if re.match(r'dec_med\d*',  c)), None)
        col_dec_pimp= next((c for c in df.columns if re.match(r'dec_pimp\d*', c)), None)

        missing = [name for name, col in {
            "iris": col_iris,
            "dec_med*": col_dec_med, "dec_pimp*": col_dec_pimp
        }.items() if col is None]

        if missing:
            continue

        # 3. Filtre Paris + sélection des colonnes détectées
        df["iris"] = df["iris"].astype(str)
        df = df[df["iris"].str.startswith("75")]
        df = df[[col_iris, col_dec_med, col_dec_pimp]]

        # 4. Renommage vers des noms stables pour SQLite
        df = df.rename(columns={
            col_iris:     "iris",
            col_dec_med:  "dec_med",
            col_dec_pimp: "dec_pimp",
        })

        # Ajout d'une colonne traçabilité (optionnel)
        dfs.append(df)

    if not dfs:
        raise ValueError("Aucun fichier valide n'a pu être traité.")

    # 5. Concaténation de tous les fichiers
    result = pd.concat(dfs)

    result["iris"] = result["iris"].astype(str)
    df_nb_habitant["iris"] = df_nb_habitant["iris"].astype(str).str.replace(r"\.0$", "", regex=True)

    result = result.merge(
        df_nb_habitant,
        on="iris",
        how="left"
    )

    


    # 6. Écriture dans SQLite
    conn = sqlite3.connect(db_path)
    result.to_sql("population_niveau_vie", conn, if_exists="replace", index=False)
    conn.close()
 



def prix_arrondissement():
    file = "stats_whole_period.parquet"
    file_path = os.path.join(f"{BASE_DIR}/KPI_impose_silver", file)
    prix_arrondissement = pd.read_parquet(file_path)

    prix_arrondissement = prix_arrondissement[(prix_arrondissement["code_geo"].str.startswith("751")) & (prix_arrondissement["echelle_geo"] == "commune")]
    conn = sqlite3.connect(db_path)
    prix_arrondissement.to_sql("prix_arrondissement", conn, if_exists="replace", index=False)
    conn.close() 



# quartiers_paris()
# activite_quartier()
#nuisance_sonore()
#disponibilite_stationnement()
#proprete_general()
#population_niveau_vie()
#location_arrondissement()
#logement_sociaux()
prix_arrondissement()
# delete table prix_arrondissement


conn.close()