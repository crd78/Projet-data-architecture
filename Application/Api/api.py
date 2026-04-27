from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from Application.Api.routers import (
    quartiers,
    logements,
    revenus,
    chantiers,
    signalements,
    stationnement,
)
from Application.Api.routers.kpis import (
    nuisance_sonore,
    stationnement_score,
    activite_quartier,
    signalements_score,
)

app = FastAPI(
    title="Paris Data API",
    description="API d'accès aux données urbaines de Paris (logements, revenus, chantiers, stationnement, signalements).",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(quartiers.router)
app.include_router(logements.router)
app.include_router(revenus.router)
app.include_router(chantiers.router)
app.include_router(signalements.router)
app.include_router(stationnement.router)

# KPIs
app.include_router(nuisance_sonore.router)
app.include_router(stationnement_score.router)
app.include_router(activite_quartier.router)
app.include_router(signalements_score.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Paris Data API — v1.0",
        "docs": "/docs",
        "endpoints": [
            "/quartiers",
            "/logements/sociaux",
            "/logements/loyers",
            "/revenus/iris",
            "/revenus/population",
            "/chantiers",
            "/signalements",
            "/signalements/types",
            "/signalements/stats",
            "/stationnement/parkings",
            "/stationnement/voie-publique",
            "/stationnement/voie-publique/stats",
            "--- KPIs ---",
            "/kpi/nuisance-sonore/{arrondissement}",
            "/kpi/stationnement/{arrondissement}",
            "/kpi/activite/{arrondissement}",
            "/kpi/signalements/score-pondere",
            "/kpi/signalements/temps-resolution",
        ],
    }
