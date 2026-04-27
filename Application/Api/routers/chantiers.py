from fastapi import APIRouter, Query
from typing import Optional
from Application.Api import data

router = APIRouter(prefix="/chantiers", tags=["Chantiers"])


@router.get("/", summary="Chantiers déclarés à Paris")
def get_chantiers(
    arrondissement: Optional[int] = Query(None, description="Arrondissement (1-20)"),
    responsable: Optional[str] = Query(None, description="Responsable du chantier"),
    annee_debut: Optional[int] = Query(None, description="Année de début (ex: 2022)"),
    impact_stationnement: Optional[str] = Query(None, description="Filtrer par impact stationnement"),
    limit: int = Query(100, ge=1, le=1000, description="Nombre max de résultats"),
):
    df = data.chantiers()
    if arrondissement is not None:
        code = f"750{arrondissement:02d}"
        df = df[df["code_postal_arrondissement_commune"] == code]
    if responsable is not None:
        df = df[df["responsable_du_chantier"].str.contains(responsable, case=False, na=False)]
    if annee_debut is not None:
        df = df[df["date_debut_du_chantier"].dt.year == annee_debut]
    if impact_stationnement is not None:
        df = df[df["impact_stationnement"].str.lower() == impact_stationnement.lower()]
    return {
        "total": len(df),
        "resultats": df.head(limit).to_dict(orient="records"),
    }
