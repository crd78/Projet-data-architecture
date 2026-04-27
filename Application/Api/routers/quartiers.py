from fastapi import APIRouter, HTTPException
from Application.Api import data

router = APIRouter(prefix="/quartiers", tags=["Quartiers"])


@router.get("/", summary="Liste des 80 quartiers parisiens")
def get_quartiers():
    df = data.quartiers()
    return df.to_dict(orient="records")


@router.get("/{c_qu}", summary="Détail d'un quartier")
def get_quartier(c_qu: int):
    df = data.quartiers()
    row = df[df["c_qu"] == c_qu]
    if row.empty:
        raise HTTPException(status_code=404, detail="Quartier non trouvé")
    return row.iloc[0].to_dict()


@router.get("/arrondissement/{arrondissement}", summary="Quartiers d'un arrondissement")
def get_quartiers_by_arrondissement(arrondissement: int):
    df = data.quartiers()
    result = df[df["c_ar"] == arrondissement]
    if result.empty:
        raise HTTPException(status_code=404, detail="Aucun quartier pour cet arrondissement")
    return result.to_dict(orient="records")
