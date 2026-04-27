from fastapi import APIRouter, Query
from typing import Optional
from Application.Api import data

router = APIRouter(prefix="/signalements", tags=["Signalements Dans Ma Rue"])


@router.get("/", summary="Signalements citoyens (Dans ma rue)")
def get_signalements(
    arrondissement: Optional[int] = Query(None, description="Arrondissement (1-20)"),
    type_declaration: Optional[str] = Query(None, description="Type de signalement"),
    annee: Optional[int] = Query(None, description="Année de déclaration"),
    mois: Optional[int] = Query(None, ge=1, le=12, description="Mois de déclaration"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre max de résultats"),
):
    df = data.signalements()
    if arrondissement is not None:
        df = df[df["arrondissement"] == arrondissement]
    if type_declaration is not None:
        df = df[df["type_declaration"].str.contains(type_declaration, case=False, na=False)]
    if annee is not None:
        df = df[df["annee_declaration"] == annee]
    if mois is not None:
        df = df[df["mois_declaration"] == mois]
    return {
        "total": len(df),
        "resultats": df.head(limit).to_dict(orient="records"),
    }


@router.get("/types", summary="Liste des types de signalements disponibles")
def get_types_signalements():
    df = data.signalements()
    types = df["type_declaration"].dropna().unique().tolist()
    return {"types": sorted(types)}


@router.get("/stats", summary="Statistiques par arrondissement")
def get_stats_signalements(
    annee: Optional[int] = Query(None, description="Filtrer par année"),
):
    df = data.signalements()
    if annee is not None:
        df = df[df["annee_declaration"] == annee]
    stats = (
        df.groupby("arrondissement")["id_declaration"]
        .count()
        .reset_index()
        .rename(columns={"id_declaration": "nb_signalements"})
        .sort_values("arrondissement")
    )
    return stats.to_dict(orient="records")
