"""
KPI 2 — Disponibilité du stationnement par arrondissement

Formule :
  score = (Places_Voirie × 0.6 + Places_Parking_Public × 0.4) / Indice_trafic

Indice_trafic : débit moyen en véh/h depuis Paris OpenData (1 si indisponible)
"""

import os
import requests
from fastapi import APIRouter, HTTPException
from Application.Api import data

router = APIRouter(prefix="/kpi/stationnement", tags=["KPI 2 - Disponibilité Stationnement"])

TRAFFIC_API = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/comptages-routiers-permanents/records"

CENTROIDS = {
    1: (48.8600, 2.3477),  2: (48.8667, 2.3503),  3: (48.8630, 2.3604),
    4: (48.8547, 2.3529),  5: (48.8458, 2.3508),  6: (48.8495, 2.3317),
    7: (48.8568, 2.3118),  8: (48.8742, 2.3070),  9: (48.8769, 2.3390),
    10: (48.8756, 2.3607), 11: (48.8593, 2.3762), 12: (48.8418, 2.3892),
    13: (48.8317, 2.3622), 14: (48.8317, 2.3248), 15: (48.8420, 2.2955),
    16: (48.8638, 2.2666), 17: (48.8883, 2.3178), 18: (48.8917, 2.3495),
    19: (48.8811, 2.3817), 20: (48.8643, 2.3990),
}


def _places_voirie(arrondissement: int) -> int:
    df = data.voie_publique()
    df = df[df["arrondissement"] == arrondissement]
    return int(df["nombre_places_reelles"].sum())


def _places_parking(arrondissement: int) -> int:
    df = data.parkings()
    df = df[df["arrondissement"] == arrondissement]
    return int(df["nbre_total_places"].sum())


def _indice_trafic(arrondissement: int) -> float:
    lat, lon = CENTROIDS.get(arrondissement, (48.8566, 2.3522))
    try:
        resp = requests.get(
            TRAFFIC_API,
            params={
                "limit": 100,
                "geofilter.distance": f"{lat},{lon},1000",
                "select": "q",
            },
            timeout=5,
        )
        resp.raise_for_status()
        records = resp.json().get("results", [])
        debits = [r["q"] for r in records if r.get("q")]
        if not debits:
            return 1.0
        debit_moyen = sum(debits) / len(debits)
        # Normalisation : 1000 veh/h = indice 1, plus c'est chargé plus l'indice monte
        return round(max(debit_moyen / 1000, 0.1), 3)
    except Exception:
        return 1.0


@router.get("/{arrondissement}", summary="Score de disponibilité du stationnement")
def get_score_stationnement(arrondissement: int):
    if arrondissement not in range(1, 21):
        raise HTTPException(status_code=400, detail="Arrondissement invalide (1-20)")

    places_voirie = _places_voirie(arrondissement)
    places_parking = _places_parking(arrondissement)
    indice_trafic = _indice_trafic(arrondissement)

    score = (places_voirie * 0.6 + places_parking * 0.4) / indice_trafic

    return {
        "arrondissement": arrondissement,
        "places_voirie": places_voirie,
        "places_parking_public": places_parking,
        "indice_trafic": indice_trafic,
        "score_disponibilite": round(score, 2),
        "formule": "(Places_Voirie × 0.6 + Places_Parking_Public × 0.4) / Indice_trafic",
    }


@router.get("/", summary="Classement de disponibilité du stationnement pour tous les arrondissements")
def get_classement_stationnement():
    resultats = []
    for arr in range(1, 21):
        places_voirie = _places_voirie(arr)
        places_parking = _places_parking(arr)
        score = (places_voirie * 0.6 + places_parking * 0.4)
        resultats.append({
            "arrondissement": arr,
            "places_voirie": places_voirie,
            "places_parking_public": places_parking,
            "score_brut": round(score, 2),
        })
    resultats.sort(key=lambda x: x["score_brut"], reverse=True)
    return resultats
