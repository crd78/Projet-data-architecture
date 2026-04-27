from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from Application.Api import data

router = APIRouter(prefix="/revenus", tags=["Revenus & Population"])

ANNEES_DISPONIBLES = [2018, 2019, 2020]


@router.get("/iris", summary="Revenus fiscaux par IRIS")
def get_revenus_iris(
    annee: int = Query(..., description="Année (2018, 2019 ou 2020)"),
    iris: Optional[str] = Query(None, description="Code IRIS"),
):
    if annee not in ANNEES_DISPONIBLES:
        raise HTTPException(
            status_code=400,
            detail=f"Année invalide. Disponible : {ANNEES_DISPONIBLES}",
        )
    df = data.revenus_iris(annee)
    if iris is not None:
        df = df[df["iris"] == iris]
        if df.empty:
            raise HTTPException(status_code=404, detail="Code IRIS non trouvé")
    return {
        "annee": annee,
        "total": len(df),
        "resultats": df.to_dict(orient="records"),
    }


@router.get("/population", summary="Structure de population par IRIS (2021)")
def get_population(
    iris: Optional[str] = Query(None, description="Code IRIS"),
    dep: Optional[str] = Query(None, description="Code département"),
):
    df = data.population()
    if iris is not None:
        df = df[df["iris"].astype(str).str.startswith(iris)]
    if dep is not None:
        df = df[df["dep"].astype(str) == dep]
    return {
        "total": len(df),
        "resultats": df.to_dict(orient="records"),
    }
