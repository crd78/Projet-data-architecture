import { getJson } from "./apiClient";

export function fetchMedianPricePerArrondissement(annee, arrondissement, mode, signal) {
  return getJson(
    "/kpi/median_price_per_arrondissement",
    {
      annee: String(annee),
      arrondissement: String(arrondissement),
      mode: mode || "location",
    },
    { signal }
  );
}

export function fetchRepartitionTypesLogements(annee, arrondissement, signal) {
  return getJson(
    "/kpi/repartition_types_logements",
    { annee: String(annee), arrondissement: String(arrondissement) },
    { signal }
  );
}

export function fetchLogementsSociauxTotal(annee, arrondissement, signal) {
  return getJson(
    "/kpi/logements_sociaux_total",
    { annee: String(annee), arrondissement: String(arrondissement) },
    { signal }
  );
}

export function fetchAccessibiliteLoyerRevenu(annee, arrondissement, revenuProportion, signal) {
  return getJson(
    "/kpi/accessibilite_loyer_revenu",
    {
      annee: String(annee),
      arrondissement: String(arrondissement),
      revenu_proportion: String(revenuProportion),
    },
    { signal }
  );
}

export function fetchDisponibiliteStationnement(longitude, latitude, signal) {
  return getJson(
    "/kpi/disponibilite_stationnement",
    {
      longitude: String(longitude),
      latitude: String(latitude),
    },
    { signal }
  );
}

export function fetchActiviteQuartier(longitude, latitude, signal) {
  return getJson(
    "/kpi/activite_quartier",
    {
      longitude: String(longitude),
      latitude: String(latitude),
    },
    { signal }
  );
}

export function fetchPropreteGenerale(longitude, latitude, signal) {
  return getJson(
    "/kpi/proprete_generale",
    {
      longitude: String(longitude),
      latitude: String(latitude),
    },
    { signal }
  );
}

export function fetchNuisanceSonore(longitude, latitude, signal) {
  return getJson(
    "/kpi/nuisance_sonore",
    {
      longitude: String(longitude),
      latitude: String(latitude),
    },
    { signal }
  );
}