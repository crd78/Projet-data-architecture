import { getJson } from "./apiClient";

export function fetchMedianPricePerArrondissement(annee, arrondissement, signal) {
  return getJson(
    "/kpi/median_price_per_arrondissement",
    { annee: String(annee), arrondissement: String(arrondissement) },
    { signal }
  );
}