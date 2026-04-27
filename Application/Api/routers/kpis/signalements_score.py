"""
KPI 4a — Temps moyen de résolution des signalements
KPI 4b — Score pondéré des déclarations par quartier / trimestre

Formule KPI 4b :
  KPI = Σ(poids_type × nb_declarations_type) / (population ou surface)

Poids par type :
  Propreté               → 1.0
  Graffitis, tags        → 0.7
  Mobiliers urbains      → 0.9
  Dégradation du sol     → 1.2
  (autres)               → 0.8  (défaut)
"""

from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from Application.Api import data

router = APIRouter(prefix="/kpi/signalements", tags=["KPI 4 - Signalements"])

POIDS_TYPE = {
    "Propreté": 1.0,
    "Graffitis, tags, affiches": 0.7,
    "Mobiliers urbains": 0.9,
    "Dégradation du sol": 1.2,
}
POIDS_DEFAUT = 0.8


# ─── KPI 4a — Temps de résolution ────────────────────────────────────────────

@router.get(
    "/temps-resolution",
    summary="Temps moyen de résolution des signalements",
)
def get_temps_resolution(
    arrondissement: Optional[int] = Query(None, description="Filtrer par arrondissement"),
    annee: Optional[int] = Query(None, description="Filtrer par année"),
    type_declaration: Optional[str] = Query(None, description="Filtrer par type de signalement"),
):
    """
    NOTE : Le dataset 'Dans ma rue' ne contient pas de date de clôture.
    Ce KPI nécessite une source complémentaire avec date_fin de traitement.
    En l'état, on retourne les statistiques disponibles (volume, délai moyen déclaration→fin de mois).
    """
    df = data.signalements()

    if arrondissement is not None:
        df = df[df["arrondissement"] == arrondissement]
    if annee is not None:
        df = df[df["annee_declaration"] == annee]
    if type_declaration is not None:
        df = df[df["type_declaration"].str.contains(type_declaration, case=False, na=False)]

    nb_total = len(df)

    return {
        "statut": "partiel",
        "message": "Le dataset 'Dans ma rue' ne contient pas de date_fin — temps de résolution non calculable depuis cette source uniquement.",
        "arrondissement": arrondissement,
        "annee": annee,
        "nb_signalements": nb_total,
        "repartition_par_type": (
            df.groupby("type_declaration")["id_declaration"]
            .count()
            .reset_index()
            .rename(columns={"id_declaration": "nb"})
            .sort_values("nb", ascending=False)
            .to_dict(orient="records")
        ),
    }


# ─── KPI 4b — Score pondéré ──────────────────────────────────────────────────

@router.get(
    "/score-pondere",
    summary="Score pondéré des déclarations par arrondissement et trimestre",
)
def get_score_pondere(
    annee: Optional[int] = Query(None, description="Filtrer par année"),
    trimestre: Optional[int] = Query(None, ge=1, le=4, description="Trimestre (1-4)"),
    normalisation: str = Query("population", description="Normaliser par 'population' ou 'surface'"),
):
    df = data.signalements()

    if annee is not None:
        df = df[df["annee_declaration"] == annee]
    if trimestre is not None:
        mois_map = {1: [1, 2, 3], 2: [4, 5, 6], 3: [7, 8, 9], 4: [10, 11, 12]}
        df = df[df["mois_declaration"].isin(mois_map[trimestre])]

    df = df.dropna(subset=["arrondissement"])
    df["arrondissement"] = df["arrondissement"].astype(int)
    df["poids"] = df["type_declaration"].map(POIDS_TYPE).fillna(POIDS_DEFAUT)
    df["contribution"] = df["poids"]

    scores = (
        df.groupby(["arrondissement", "type_declaration"])
        .agg(nb=("id_declaration", "count"), poids=("poids", "first"))
        .reset_index()
    )
    scores["score_type"] = scores["nb"] * scores["poids"]

    score_par_arr = (
        scores.groupby("arrondissement")["score_type"]
        .sum()
        .reset_index()
        .rename(columns={"score_type": "score_brut"})
    )

    if normalisation == "population":
        pop = data.population()[["iris", "p21_pop"]].copy()
        # Les codes IRIS commencent par 751XX pour Paris (XX = arrondissement)
        pop["arrondissement"] = pop["iris"].apply(
            lambda x: int(str(x)[:5][3:]) if str(x)[:3] == "751" else None
        )
        pop = pop.dropna(subset=["arrondissement"])
        pop["arrondissement"] = pop["arrondissement"].astype(int)
        pop_arr = pop.groupby("arrondissement")["p21_pop"].sum().reset_index()
        score_par_arr = score_par_arr.merge(pop_arr, on="arrondissement", how="left")
        score_par_arr["score_normalise"] = (
            score_par_arr["score_brut"] / score_par_arr["p21_pop"].replace(0, 1)
        ).round(6)
    else:
        df_quartiers = data.quartiers()
        surface_arr = (
            df_quartiers.groupby("c_ar")["surface"]
            .sum()
            .reset_index()
            .rename(columns={"c_ar": "arrondissement"})
        )
        score_par_arr = score_par_arr.merge(surface_arr, on="arrondissement", how="left")
        score_par_arr["score_normalise"] = (
            score_par_arr["score_brut"] / score_par_arr["surface"].replace(0, 1)
        ).round(6)

    score_par_arr = score_par_arr.sort_values("score_normalise", ascending=False)

    return {
        "annee": annee,
        "trimestre": trimestre,
        "normalisation": normalisation,
        "poids_utilises": POIDS_TYPE,
        "formule": "Σ(poids_type × nb_declarations_type) / (population ou surface)",
        "resultats": score_par_arr.to_dict(orient="records"),
    }


@router.get(
    "/score-pondere/types",
    summary="Poids utilisés par type de déclaration",
)
def get_poids():
    return {"poids": POIDS_TYPE, "poids_defaut": POIDS_DEFAUT}
