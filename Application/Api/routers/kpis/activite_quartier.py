"""
KPI 3 — Activité dans le quartier par arrondissement

Sources : Google Places API (restaurants, commerces, épiceries)

Formule :
  score = (nb_lieux × 2) + (moyenne_notes × 10) - (lieux_fermés × 5)
"""

import os
import requests
from fastapi import APIRouter, HTTPException, Query
from typing import Optional

router = APIRouter(prefix="/kpi/activite", tags=["KPI 3 - Activité Quartier"])

GOOGLE_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")
PLACES_URL = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"

PLACE_TYPES = ["restaurant", "store", "grocery_or_supermarket", "cafe", "bakery"]

CENTROIDS = {
    1: (48.8600, 2.3477),  2: (48.8667, 2.3503),  3: (48.8630, 2.3604),
    4: (48.8547, 2.3529),  5: (48.8458, 2.3508),  6: (48.8495, 2.3317),
    7: (48.8568, 2.3118),  8: (48.8742, 2.3070),  9: (48.8769, 2.3390),
    10: (48.8756, 2.3607), 11: (48.8593, 2.3762), 12: (48.8418, 2.3892),
    13: (48.8317, 2.3622), 14: (48.8317, 2.3248), 15: (48.8420, 2.2955),
    16: (48.8638, 2.2666), 17: (48.8883, 2.3178), 18: (48.8917, 2.3495),
    19: (48.8811, 2.3817), 20: (48.8643, 2.3990),
}


def _fetch_places(lat: float, lon: float, place_type: str, radius: int = 1000) -> list:
    if not GOOGLE_API_KEY:
        return []
    try:
        resp = requests.get(
            PLACES_URL,
            params={
                "location": f"{lat},{lon}",
                "radius": radius,
                "type": place_type,
                "key": GOOGLE_API_KEY,
            },
            timeout=5,
        )
        resp.raise_for_status()
        return resp.json().get("results", [])
    except Exception:
        return []


def _calcul_score(lieux: list) -> dict:
    nb_lieux = len(lieux)
    notes = [r["rating"] for r in lieux if r.get("rating")]
    nb_fermes = sum(
        1 for r in lieux
        if r.get("opening_hours", {}).get("open_now") is False
    )
    moyenne_notes = round(sum(notes) / len(notes), 2) if notes else 0.0
    score = (nb_lieux * 2) + (moyenne_notes * 10) - (nb_fermes * 5)

    return {
        "nb_lieux": nb_lieux,
        "moyenne_notes": moyenne_notes,
        "nb_fermes": nb_fermes,
        "score": round(score, 2),
    }


@router.get("/{arrondissement}", summary="Score d'activité d'un arrondissement")
def get_activite(
    arrondissement: int,
    radius: int = Query(1000, ge=200, le=2000, description="Rayon de recherche en mètres"),
):
    if arrondissement not in range(1, 21):
        raise HTTPException(status_code=400, detail="Arrondissement invalide (1-20)")
    if not GOOGLE_API_KEY:
        raise HTTPException(
            status_code=503,
            detail="GOOGLE_PLACES_API_KEY non configurée. Définissez la variable d'environnement.",
        )

    lat, lon = CENTROIDS[arrondissement]
    tous_lieux = []
    par_type = {}

    for place_type in PLACE_TYPES:
        lieux = _fetch_places(lat, lon, place_type, radius)
        par_type[place_type] = _calcul_score(lieux)
        tous_lieux.extend(lieux)

    # Dédoublonnage par place_id
    vus = set()
    lieux_uniques = []
    for l in tous_lieux:
        pid = l.get("place_id")
        if pid and pid not in vus:
            vus.add(pid)
            lieux_uniques.append(l)

    score_global = _calcul_score(lieux_uniques)

    return {
        "arrondissement": arrondissement,
        "radius_m": radius,
        "score_global": score_global,
        "detail_par_type": par_type,
        "formule": "(nb_lieux × 2) + (moyenne_notes × 10) - (lieux_fermés × 5)",
    }
