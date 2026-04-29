import { formatNumber } from "../../utils/formatters";

function formatAchat(value) {
  if (value === null || value === undefined) return "—";
  return Number(value) / 4;
}

function KpiMedianPricesCard({
  selectedArrondissement,
  medianLocation,
  medianLocationLoading,
  medianLocationError,
  medianAchat,
  medianAchatLoading,
  medianAchatError
}) {
  return (
    <div className="rounded-lg border border-blue-100 bg-white p-3 text-slate-700">
      <div className="font-semibold">Prix médian (€/m²)</div>

      {selectedArrondissement === "all" && (
        <div className="mt-2 text-sm text-slate-500">
          Veuillez sélectionner un arrondissement
        </div>
      )}

      {selectedArrondissement !== "all" && (
        <div className="mt-3 grid grid-cols-2 gap-4">
          <div>
            <div className="text-xs text-slate-500">Location</div>
            {medianLocationLoading && (
              <div className="text-sm text-slate-500">Chargement…</div>
            )}
            {!!medianLocationError && (
              <div className="text-sm text-red-600">Erreur : {medianLocationError}</div>
            )}
            {!medianLocationLoading && !medianLocationError && (
              <div className="text-2xl font-bold text-blue-900">
                {formatNumber(medianLocation?.median_price_loyer, 2)}
              </div>
            )}
          </div>

          <div>
            <div className="text-xs text-slate-500">Achat</div>
            {medianAchatLoading && (
              <div className="text-sm text-slate-500">Chargement…</div>
            )}
            {!!medianAchatError && (
              <div className="text-sm text-red-600">Erreur : {medianAchatError}</div>
            )}
            {!medianAchatLoading && !medianAchatError && (
              <div className="text-2xl font-bold text-blue-900">
                {formatNumber(formatAchat(medianAchat?.median_price_achat), 2)}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default KpiMedianPricesCard;