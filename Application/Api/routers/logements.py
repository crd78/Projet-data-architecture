from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from Application.Api import data

router = APIRouter(prefix="/logements", tags=["Logements"])


@router.get("/sociaux", summary="Logements sociaux financés à Paris")
def get_logements_sociaux(
    arrondissement: Optional[int] = Query(None, description="Numéro d'arrondissement (1-20)"),
    annee: Optional[int] = Query(None, description="Année de financement"),
    bailleur: Optional[str] = Query(None, description="Nom du bailleur social"),
):
    df = data.logements_sociaux()
    if arrondissement is not None:
        df = df[df["arrondissement"] == arrondissement]
    if annee is not None:
        df = df[df["annee_du_financement_agrement"] == annee]
    if bailleur is not None:
        df = df[df["bailleur_social"].str.contains(bailleur, case=False, na=False)]
    return {
        "total": len(df),
        "resultats": df.to_dict(orient="records"),
    }


@router.get("/loyers", summary="Encadrement des loyers par quartier")
def get_loyers(
    annee: Optional[int] = Query(None, description="Année"),
    numero_quartier: Optional[int] = Query(None, description="Numéro du quartier"),
    nb_pieces: Optional[int] = Query(None, description="Nombre de pièces principales"),
    type_location: Optional[str] = Query(None, description="Type de location (meublé / vide)"),
):
    df = data.loyers()
    if annee is not None:
        df = df[df["annee"] == annee]
    if numero_quartier is not None:
        df = df[df["numero_du_quartier"] == numero_quartier]
    if nb_pieces is not None:
        df = df[df["nombre_de_pieces_principales"] == nb_pieces]
    if type_location is not None:
        df = df[df["type_de_location"].str.lower() == type_location.lower()]
    return {
        "total": len(df),
        "resultats": df.to_dict(orient="records"),
    }
