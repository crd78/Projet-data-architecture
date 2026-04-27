"""
KPI 1 — Score de nuisance sonore par arrondissement

Sources :
  - Chantiers (local parquet Silver)
  - Densité du trafic (Paris OpenData API)
  - Bars / boîtes de nuit (Google Places API)

Formule chantiers :
  dB_estimé = dB_base + k × log10(1 + surface_m2)
"""

import math
import os
import requests
from fastapi import APIRouter, Query, HTTPException
from Application.Api import data

router = APIRouter(prefix="/kpi/nuisance-sonore", tags=["KPI 1 - Nuisance Sonore"])

DB_BASE = 65.0
K = 10.0

GOOGLE_API_KEY = os.getenv("GOOGLE_PLACES_API_KEY", "")
TRAFFIC_API = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/comptages-routiers-permanents/records"

# Centroïdes approximatifs des arrondissements parisiens
CENTROIDS = {
    1: (48.8600, 2.3477),  2: (48.8667, 2.3503),  3: (48.8630, 2.3604),
    4: (48.8547, 2.3529),  5: (48.8458, 2.3508),  6: (48.8495, 2.3317),
    7: (48.8568, 2.3118),  8: (48.8742, 2.3070),  9: (48.8769, 2.3390),
    10: (48.8756, 2.3607), 11: (48.8593, 2.3762), 12: (48.8418, 2.3892),
    13: (48.8317, 2.3622), 14: (48.8317, 2.3248), 15: (48.8420, 2.2955),
    16: (48.8638, 2.2666), 17: (48.8883, 2.3178), 18: (48.8917, 2.3495),
    19: (48.8811, 2.3817), 20: (48.8643, 2.3990),
}


def _score_chantiers(arrondissement: int) -> dict:
    df = data.chantiers()
    code = f"750{arrondissement:02d}"
    df = df[df["code_postal_arrondissement_commune"] == code].dropna(subset=["surface_m2"])

    if df.empty:
        return {"nb_chantiers": 0, "db_estime_moyen": DB_BASE, "surface_totale_m2": 0}

    df = df.copy()
    df["db_estime"] = df["surface_m2"].apply(lambda s: DB_BASE + K * math.log10(1 + s))

    return {
        "nb_chantiers": len(df),
        "db_estime_moyen": round(df["db_estime"].mean(), 2),
        "surface_totale_m2": round(df["surface_m2"].sum(), 2),
    }


def _fetch_traffic(arrondissement: int) -> dict:
    lat, lon = CENTROIDS.get(arrondissement, (48.8566, 2.3522))
    try:
        resp = requests.get(
            TRAFFIC_API,
            params={
                "limit": 100,
                "geofilter.distance": f"{lat},{lon},1000",
                "select": "q,etat_trafic",
            },
            timeout=5,
        )
        resp.raise_for_status()
        records = resp.json().get("results", [])
        debits = [r["q"] for r in records if r.get("q") is not None]
        return {
            "nb_capteurs": len(records),
            "debit_moyen_veh_h": round(sum(debits) / len(debits), 1) if debits else None,
            "etats": {
                e: sum(1 for r in records if r.get("etat_trafic") == e)
                for e in ["libre", "dense", "sature", "bloquant"]
            },
        }
    except Exception as exc:
        return {"erreur": str(exc), "debit_moyen_veh_h": None}


def _fetch_bars_clubs(arrondissement: int) -> dict:
    if not GOOGLE_API_KEY:
        return {"erreur": "GOOGLE_PLACES_API_KEY non configurée", "count": None}
    lat, lon = CENTROIDS.get(arrondissement, (48.8566, 2.3522))
    try:
        resp = requests.get(
            "https://maps.googleapis.com/maps/api/place/nearbysearch/json",
            params={
                "location": f"{lat},{lon}",
                "radius": 1000,
                "type": "bar|night_club",
                "key": GOOGLE_API_KEY,
            },
            timeout=5,
        )
        resp.raise_for_status()
        results = resp.json().get("results", [])
        return {
            "count": len(results),
            "lieux": [{"nom": r["name"], "note": r.get("rating")} for r in results[:10]],
        }
    except Exception as exc:
        return {"erreur": str(exc), "count": None}


@router.get("/{arrondissement}", summary="Score de nuisance sonore d'un arrondissement")
def get_nuisance_sonore(arrondissement: int):
    if arrondissement not in range(1, 21):
        raise HTTPException(status_code=400, detail="Arrondissement invalide (1-20)")

    chantiers = _score_chantiers(arrondissement)
    trafic = _fetch_traffic(arrondissement)
    bars = _fetch_bars_clubs(arrondissement)

    return {
        "arrondissement": arrondissement,
        "chantiers": chantiers,
        "trafic": trafic,
        "bars_boites_de_nuit": bars,
    }


@router.get("/", summary="Score de nuisance sonore pour tous les arrondissements")
def get_nuisance_sonore_tous(
    inclure_trafic: bool = Query(False, description="Inclure l'appel à l'API trafic (plus lent)"),
    inclure_bars: bool = Query(False, description="Inclure l'appel Google Places (nécessite clé API)"),
):
    resultats = []
    for arr in range(1, 21):
        chantiers = _score_chantiers(arr)
        row = {"arrondissement": arr, "chantiers": chantiers}
        if inclure_trafic:
            row["trafic"] = _fetch_traffic(arr)
        if inclure_bars:
            row["bars_boites_de_nuit"] = _fetch_bars_clubs(arr)
        resultats.append(row)
    return resultats
