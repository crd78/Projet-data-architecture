from fastapi import APIRouter, Request, Query

router = APIRouter()

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
            "annee": annee,
            "secteurs_geographiques": arrondissement,
            "nombre_de_pieces_principales": {"$type": "number"},
        }},
        {"$group": {
            "_id": None,
            "median_price_loyer": {
                "$median": {"input": "$loyers_de_reference", "method": "approximate"}
            },
            "count": {"$sum": 1},
        }},
        {"$project": {
            "_id": 0,
            "count": 1,
            "median_price_loyer": {"$round": ["$median_price_loyer", 2]},
        }},
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
    
@router.get("/repartition_types_logements")
def repartition_types_logements(
    request: Request,
    annee: int = Query(..., ge=2019, le=2023, description="Année"),
    arrondissement: int = Query(..., ge=1, le=20, description="Arrondissement de Paris"),
):
    db = request.app.state.mongo_db
    collection = db["location_arrondissement"]

    pipeline = [
        {
            "$match": {
                "annee": annee,
                "secteurs_geographiques": arrondissement,
                "loyers_de_reference": {"$type": "number"},
            }
        },
        
        # Comptage par nombre de pièces
        {"$group": {"_id": "$nombre_de_pieces_principales", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
        
        # Total
        {
            "$group": {
                "_id": None,
                "total": {"$sum": "$count"},
                "items": {"$push": {"pieces": "$_id", "count": "$count"}},
            }
        },
        
        # Calcul des pourcentages
        {
            "$project": {
                "_id": 0,
                "total": 1,
                    "logements_repartition": {
                    "$map": {
                        "input": "$items",
                        "as": "it",
                        "in": {
                            "type": {"$concat": ["T", {"$toString": "$$it.pieces"}]},
                            "pieces": "$$it.pieces",
                            "count": "$$it.count",
                            "percentage": {
                                "$round": [
                                    {"$multiply": [{"$divide": ["$$it.count", "$total"]}, 100]},
                                    2,
                                ]
                            },
                        },
                    }
                },
            }
        },
    ]

    result = list(collection.aggregate(pipeline))
    if not result:
        return {
            "annee": annee,
            "arrondissement": arrondissement,
            "total": 0,
            "logements_repartition": [],
        }

    return {"annee": annee, "arrondissement": arrondissement, **result[0]}

@router.get("/accessibilite_loyer_revenu")
def accessibilite_loyer_revenu(
    request: Request,
    annee: int = Query(..., ge=2019, le=2023, description="Année"),
    arrondissement: int = Query(..., ge=1, le=20, description="Arrondissement"),
    revenu_proportion: float = Query(
        0.4,
        ge=0.05,
        le=0.8,
        description="Part du revenu mensuel utilisée pour payer le loyer (0.4 = 40%)",
    ),
):
    db = request.app.state.mongo_db

    # Loyer médian au m²
    loyers = db["location_arrondissement"]
    loyer_pipeline = [
        {
            "$match": {
                "annee": annee,
                "secteurs_geographiques": arrondissement,
                "loyers_de_reference": {"$type": "number"},
            }
        },
        {
            "$group": {
                "_id": None,
                "loyer_m2_median": {
                    "$median": {"input": "$loyers_de_reference", "method": "approximate"}
                },
                "n_loyers": {"$sum": 1},
            }
        },
        {"$project": {
            "_id": 0,
            "n_loyers": 1,
            "loyer_m2_median": {"$round": ["$loyer_m2_median", 2]},
        }},
    ]

    loyer_res = list(loyers.aggregate(loyer_pipeline))
    if not loyer_res:
        return {
            "reason": "no_loyer_data",
            "annee": annee,
            "arrondissement": arrondissement,
        }

    loyer_m2 = loyer_res[0]["loyer_m2_median"]

    # Revenu annuel médian 
    revenus = db["population_niveau_vie"]
    iris_prefix = f"751{arrondissement:02d}"

    revenu_pipeline = [
        {"$match": {"iris": {"$regex": f"^{iris_prefix}"}}},
        {"$addFields": {
            "dec_med_num": {
                "$convert": {"input": "$dec_med", "to": "double", "onError": None, "onNull": None}
            }
        }},
        {"$match": {"dec_med_num": {"$ne": None}}},
        {
            "$group": {
                "_id": None,
                "income_annual_avg_of_iris_medians": {"$avg": "$dec_med_num"},
                "n_iris": {"$sum": 1},
            }
        },
        {"$project": {"_id": 0}},
    ]

    revenu_res = list(revenus.aggregate(revenu_pipeline))
    if not revenu_res or revenu_res[0].get("income_annual_avg_of_iris_medians") is None:
        return {
            "reason": "no_income_data",
            "annee": annee,
            "arrondissement": arrondissement,
        }

    income_annual = revenu_res[0]["income_annual_avg_of_iris_medians"]
    income_monthly = income_annual / 12.0

    # Formule de calcul de l'accessibilité : m² louable = (proportion du revenu * revenu_mensuel) / loyer_m2
    m2_accessible = (revenu_proportion * income_monthly) / loyer_m2 if loyer_m2 else None

    return {
        "annee": annee,
        "arrondissement": arrondissement,
        "loyer_m2_median": round(loyer_m2, 2) if loyer_m2 is not None else None,
        "income_monthly": round(income_monthly, 2),
        "revenu_proportion": revenu_proportion,
        "m2_accessible": round(m2_accessible, 2) if m2_accessible is not None else None,
    }

@router.get("/logements_sociaux_total")
def logements_sociaux_total(
    request: Request,
    annee: int = Query(..., description="Année (annee_du_financement_agrement)"),
    arrondissement: int | None = Query(None, ge=1, le=20, description="Optionnel"),
):
    db = request.app.state.mongo_db
    col = db["logement_sociaux"]

    match = {"annee_du_financement_agrement": annee}
    if arrondissement is not None:
        match["arrondissement"] = arrondissement

    pipeline = [
        {"$match": match},
        {"$group": {
            "_id": None,
            "logements_sociaux_finances_total": {"$sum": "$nombre_total_de_logements_finances"},
            "programmes_count": {"$sum": 1},
        }},
        {"$project": {"_id": 0}},
    ]

    res = list(col.aggregate(pipeline))
    if not res:
        return {
            "annee": annee,
            "arrondissement": arrondissement,
            "logements_sociaux_finances_total": 0,
            "programmes_count": 0,
        }

    return {"annee": annee, "arrondissement": arrondissement, **res[0]}
   