from fastapi import APIRouter, Request, Query

router = APIRouter()

@router.get("/test")
def test_mongo(request: Request):
    db = request.app.state.mongo_db
    collections = db.list_collection_names()
    return {
        "status": "ok",
        "db": db.name,
        "collections_count": len(collections),
        "collections_sample": collections[:10],
    }

@router.get("/median_price_per_arrondissement")
def median_per_arrondissement(
        request: Request,
        annee: int = Query(..., ge=2019, le=2023, description="Année"),
        arrondissement: int = Query(..., ge=1, le=20, description="Arrondissement de Paris"),
    ):
    db = request.app.state.mongo_db
    collection = db["location_arrondissement"]
    pipeline = [
        {"$match": {
            "$or": [
                {"annee": annee, "secteurs_geographiques": arrondissement},
            ],
            "loyers_de_reference": {"$type": "number"},
        }},
        {"$group": {
            "_id": None,
            "median_price_loyer": {
                "$median": {"input": "$loyers_de_reference", "method": "approximate"}
            },
            "count": {"$sum": 1},
        }},
        {"$project": {"_id": 0}},
    ]
    
    result = list(collection.aggregate(pipeline))
    if not result:
        return {
            "annee": annee,
            "arrondissement": arrondissement,
            "count": 0,
            "median_price_loyer": None,
        }

    return {
        "annee": annee,
        "arrondissement": arrondissement,
        **result[0],
    }
    
    
    