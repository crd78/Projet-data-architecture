from fastapi import APIRouter, Request, Query
from .utils import extract_polygon
from shapely.geometry import Point, Polygon

router = APIRouter()


def avg_number(docs, field, digits=2):
    values = [float(d.get(field)) for d in docs if isinstance(d.get(field), (int, float))]
    return round(sum(values) / len(values), digits) if values else None


def _find_nearby_quartiers(quartiers_col, longitude: float, latitude: float, radius: float) -> list[str]:
    point = Point(longitude, latitude)
    buffer = point.buffer(radius)
    quartiers = []

    for q in quartiers_col.find({}):
        geometry = q.get("geometry") or q.get("geo_shape")
        if not geometry:
            continue

        try:
            coords = extract_polygon(geometry)
            if not coords or len(coords) < 3:
                continue

            poly = Polygon(coords)
            if poly.intersects(buffer):
                name = q.get("nom_quartier") or q.get("l_qu")
                if name and name not in quartiers:
                    quartiers.append(name)
        except Exception:
            continue

    return quartiers


@router.get("/median_price_per_arrondissement")
def median_per_arrondissement(
    request: Request,
    annee: int = Query(..., ge=2019, le=2023, description="Année"),
    arrondissement: int = Query(
        ..., ge=1, le=20, description="Arrondissement de Paris"
    ),
    mode: str = Query(
        "location", pattern="^(location|achat)$", description="location|achat"
    ),
):
    db = request.app.state.mongo_db

    if mode == "location":
        collection = db["location_arrondissement"]
        pipeline = [
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
                    "median_price_loyer": {
                        "$median": {
                            "input": "$loyers_de_reference",
                            "method": "approximate",
                        }
                    },
                    "count": {"$sum": 1},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "count": 1,
                    "median_price_loyer": {"$round": ["$median_price_loyer", 2]},
                }
            },
        ]

        result = list(collection.aggregate(pipeline))
        if not result:
            return {
                "annee": annee,
                "arrondissement": arrondissement,
                "mode": mode,
                "count": 0,
                "median_price_loyer": None,
            }

        return {
            "annee": annee,
            "arrondissement": arrondissement,
            "mode": mode,
            **result[0],
        }

    # mode == "achat"
    code_geo = f"751{arrondissement:02d}"
    doc = db["prix_arrondissement"].find_one(
        {"code_geo": code_geo},
        {"med_prix_m2_whole_apt_maison": 1, "_id": 0},
    )

    price = doc.get("med_prix_m2_whole_apt_maison") if doc else None
    return {
        "annee": annee,
        "arrondissement": arrondissement,
        "mode": mode,
        "median_price_achat": price,
        "source_period": "whole_period",
    }


@router.get("/repartition_types_logements")
def repartition_types_logements(
    request: Request,
    annee: int = Query(..., ge=2019, le=2023, description="Année"),
    arrondissement: int = Query(
        ..., ge=1, le=20, description="Arrondissement de Paris"
    ),
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
                                    {
                                        "$multiply": [
                                            {"$divide": ["$$it.count", "$total"]},
                                            100,
                                        ]
                                    },
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
                    "$median": {
                        "input": "$loyers_de_reference",
                        "method": "approximate",
                    }
                },
                "n_loyers": {"$sum": 1},
            }
        },
        {
            "$project": {
                "_id": 0,
                "n_loyers": 1,
                "loyer_m2_median": {"$round": ["$loyer_m2_median", 2]},
            }
        },
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
        {
            "$addFields": {
                "dec_med_num": {
                    "$convert": {
                        "input": "$dec_med",
                        "to": "double",
                        "onError": None,
                        "onNull": None,
                    }
                }
            }
        },
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
    m2_accessible = (
        (revenu_proportion * income_monthly) / loyer_m2 if loyer_m2 else None
    )

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
        {
            "$group": {
                "_id": None,
                "logements_sociaux_finances_total": {
                    "$sum": "$nombre_total_de_logements_finances"
                },
                "programmes_count": {"$sum": 1},
            }
        },
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


@router.get("/nuisance_sonore")
def nuisance_sonore(
    request: Request,
    longitude: float = Query(...),
    latitude: float = Query(...),
    radius: float = Query(0.03),
):

    db = request.app.state.mongo_db
    collection = db["nuisance_sonore"]

    point = Point(longitude, latitude)

    docs = collection.find({})

    selected = []

    for doc in docs:
        geometry = doc.get("geometry") or doc.get("geo_shape")
        if not geometry:
            continue

        coords = extract_polygon(geometry)
        if not coords or len(coords) < 3:
            continue

        try:
            point = Point(longitude, latitude)

            # projeter en mètres
            poly = Polygon(coords)
            buffer = point.buffer(radius)
            if poly.intersects(buffer):
                selected.append(doc)
        except Exception:
            continue

    if not selected:
        return {
            "count": 0,
            "message": "Aucune informations autour de ce lieu",
        }

    avg_coef_nature = avg_number(selected, "coef_nature_travaux")
    avg_coef_encombrant = avg_number(selected, "coef_encombrant")
    avg_nuisance_score = avg_number(selected, "nuisance_sonore_score")
    avg_db_base = avg_number(selected, "db_base")

    return {
        "count": len(selected),
        "avg_coef_nature_travaux": avg_coef_nature,
        "avg_coef_encombrant": avg_coef_encombrant,
        "avg_db_base": avg_db_base,
        "avg_nuisance_sonore_score": avg_nuisance_score,
        "score_scale": "0-100",
        "score_interpretation": "100 = nuisance sonore elevee",
    }


@router.get("/disponibilite_stationnement")
def disponibilite_stationnement(
    request: Request,
    longitude: float = Query(...),
    latitude: float = Query(...),
    radius: float = Query(0.01),
):
    db = request.app.state.mongo_db

    quartiers_col = db["quartiers_paris"]
    parking_col = db["disponibilite_stationnement"]

    quartiers_proches = _find_nearby_quartiers(quartiers_col, longitude, latitude, radius)

    if not quartiers_proches:
        return {
            "count_quartiers": 0,
            "message": "Aucun quartier dans le périmètre",
        }

    # récupérer les documents en liste pour réutilisation
    docs_list = list(parking_col.find({"nom_quartier": {"$in": quartiers_proches}}))
    if not docs_list:
        return {
            "quartiers": quartiers_proches,
            "message": "Aucune donnée stationnement",
        }

    # agrégations simples
    total_places_voirie = sum(
        (d.get("nombre_places_voirie", 0) or 0) for d in docs_list
    )
    total_places_parking_public = sum(
        (d.get("nombre_places_parking_public", 0) or 0) for d in docs_list
    )
    trafics = [float(d.get("indice_trafic_quartier") or 0) for d in docs_list]
    scores = [
        float(d.get("disponibilite_stationnement_score"))
        for d in docs_list
        if isinstance(d.get("disponibilite_stationnement_score"), (int, float))
    ]

    count = len(docs_list)
    indice_trafic_moyen = round(sum(trafics) / count, 2) if count else None
    avg_score = round(sum(scores) / len(scores), 2) if scores else None

    return {
        "quartiers": quartiers_proches,
        "count_quartiers": len(quartiers_proches),
        "nombre_places_voirie": total_places_voirie,
        "nombre_places_parking_public": total_places_parking_public,
        "indice_trafic_quartier_moyen": indice_trafic_moyen,
        "disponibilite_stationnement_score_moyen": avg_score,
        "score_scale": "0-100",
        "score_interpretation": "100 = meilleure disponibilite",
    }


@router.get("/activite_quartier")
def activite_quartier(
    request: Request,
    longitude: float = Query(...),
    latitude: float = Query(...),
    radius: float = Query(0.01),
):
    db = request.app.state.mongo_db

    quartiers_col = db["quartiers_paris"]
    activite_col = db["activite_quartier"]

    quartiers_proches = sorted(
        _find_nearby_quartiers(quartiers_col, longitude, latitude, radius)
    )

    if not quartiers_proches:
        return {
            "count_quartiers": 0,
            "message": "Aucun quartier dans le périmètre",
        }

    docs_list = list(activite_col.find({"nom_quartier": {"$in": quartiers_proches}}))
    if not docs_list:
        return {
            "quartiers": quartiers_proches,
            "message": "Aucune donnée activité",
        }

    scores = [
        float(d.get("activite_quartier_score"))
        for d in docs_list
        if isinstance(d.get("activite_quartier_score"), (int, float))
    ]
    gp_ratings = [float(d.get("gp_rating") or 0) for d in docs_list]
    gp_user_counts = [float(d.get("gp_user_rating_count") or 0) for d in docs_list]
    opens = [int(d.get("open") or 0) for d in docs_list]
    closes = [int(d.get("close") or 0) for d in docs_list]

    count = len(docs_list)
    total_score = sum(scores)
    total_gp_rating = sum(gp_ratings)
    total_gp_user_rating_count = sum(gp_user_counts)
    total_open = sum(opens)
    total_close = sum(closes)

    avg_score = round(total_score / len(scores), 2) if scores else None

    return {
        "quartiers": quartiers_proches,
        "count_quartiers": len(quartiers_proches),
        "activite_quartier_score_moyen": avg_score,
        "gp_rating_moyen": round(total_gp_rating / count, 2) if count else 0.0,
        "gp_user_rating_count_total": total_gp_user_rating_count,
        "open_total": total_open,
        "close_total": total_close,
        "score_scale": "0-100",
        "score_interpretation": "100 = activite de quartier elevee",
    }


@router.get("/proprete_generale")
def proprete_generale(
    request: Request,
    longitude: float = Query(...),
    latitude: float = Query(...),
    radius: float = Query(0.01),  # ~1km
):
    db = request.app.state.mongo_db

    quartiers_col = db["quartiers_paris"]
    proprete_col = db["proprete_general"]

    quartiers_proches = _find_nearby_quartiers(quartiers_col, longitude, latitude, radius)

    if not quartiers_proches:
        return {
            "count_quartiers": 0,
            "message": "Aucun quartier dans le périmètre",
        }

    docs = list(proprete_col.find({"nom_quartier": {"$in": quartiers_proches}}))

    total_score = 0
    count_score = 0
    count = 0
    decl_totaux = {}

    for d in docs:
        if isinstance(d.get("proprete_score"), (int, float)):
            total_score += d["proprete_score"]
            count_score += 1

        for k, v in d.items():
            if k.startswith("decl_"):
                decl_totaux[k] = decl_totaux.get(k, 0) + (v or 0)

        count += 1

    if count == 0:
        return {
            "quartiers": quartiers_proches,
            "message": "Aucune donnée propreté",
        }

    return {
        "quartiers": quartiers_proches,
        "count_quartiers": len(quartiers_proches),
        "proprete_score_moyen": (
            round(total_score / count_score, 2)
            if count_score
            else None
        ),
        "decl_totaux": decl_totaux,
        "score_scale": "0-100",
        "score_interpretation": "100 = meilleure proprete",
    }
