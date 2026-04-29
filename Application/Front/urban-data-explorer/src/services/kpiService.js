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