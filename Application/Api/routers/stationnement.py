from fastapi import APIRouter, Query, HTTPException
from typing import Optional
from Application.Api import data

router = APIRouter(prefix="/stationnement", tags=["Stationnement"])


@router.get("/parkings", summary="Parkings publics parisiens")
def get_parkings(
    arrondissement: Optional[int] = Query(None, description="Arrondissement (1-20)"),
    gratuit: Optional[bool] = Query(None, description="Filtrer les parkings gratuits"),
    pmr: Optional[bool] = Query(None, description="Filtrer ceux avec places PMR"),
    velo: Optional[bool] = Query(None, description="Filtrer ceux avec places vélo"),
):
    df = data.parkings()
    if arrondissement is not None:
        df = df[df["arrondissement"] == arrondissement]
    if gratuit is not None:
        df = df[df["gratuit"] == int(gratuit)]
    if pmr is True:
        df = df[df["nbre_place_pmr"] > 0]
    if velo is True:
        df = df[df["nbre_place_velo"] > 0]
    return {
        "total": len(df),
        "resultats": df.to_dict(orient="records"),
    }


@router.get("/parkings/{identifiant}", summary="Détail d'un parking")
def get_parking(identifiant: str):
    df = data.parkings()
    row = df[df["identifiant"] == identifiant]
    if row.empty:
        raise HTTPException(status_code=404, detail="Parking non trouvé")
    return row.iloc[0].to_dict()


@router.get("/voie-publique", summary="Emplacements de stationnement sur voie publique")
def get_voie_publique(
    arrondissement: Optional[int] = Query(None, description="Arrondissement (1-20)"),
    type_stationnement: Optional[str] = Query(None, description="Type de stationnement"),
    zone_residentielle: Optional[str] = Query(None, description="Zone résidentielle"),
    limit: int = Query(100, ge=1, le=5000, description="Nombre max de résultats"),
):
    df = data.voie_publique()
    if arrondissement is not None:
        df = df[df["arrondissement"] == arrondissement]
    if type_stationnement is not None:
        df = df[df["type_de_stationnement"].str.contains(type_stationnement, case=False, na=False)]
    if zone_residentielle is not None:
        df = df[df["zones_residentielles"].str.contains(zone_residentielle, case=False, na=False)]
    return {
        "total": len(df),
        "resultats": df.head(limit).to_dict(orient="records"),
    }


@router.get("/voie-publique/stats", summary="Capacité de stationnement par arrondissement")
def get_stats_voie_publique():
    df = data.voie_publique()
    stats = (
        df.groupby("arrondissement")[["nombre_places_calculees", "nombre_places_reelles"]]
        .sum()
        .reset_index()
        .sort_values("arrondissement")
    )
    return stats.to_dict(orient="records")
