import { formatPercent, formatSqm } from "../../utils/formatters";

function KpiAccessibiliteCard({
  selectedArrondissement,
  revenuProportion,
  onRevenuProportionChange,
  accessibiliteKpi,
  accessibiliteLoading,
  accessibiliteError
}) {
  return (
    <div className="rounded-lg border border-blue-100 bg-white p-3 text-slate-700">
      <div className="font-semibold">Accessibilité (m² louables)</div>

      {selectedArrondissement === "all" && (
        <div className="mt-2 text-sm text-slate-500">
          Sélectionne un arrondissement pour afficher la KPI.
        </div>
      )}

      <div className="mt-2 text-xs text-slate-500">
        Part du revenu utilisée : {formatPercent(revenuProportion * 100, 0)}
      </div>
      <input
        type="range"
        min="0.1"
        max="0.8"
        step="0.05"
        value={revenuProportion}
        onChange={(e) => onRevenuProportionChange(Number(e.target.value))}
        className="mt-1 w-full accent-blue-700"
      />

      {accessibiliteLoading && (
        <div className="mt-2 text-sm text-slate-500">Chargement…</div>
      )}

      {!!accessibiliteError && (
        <div className="mt-2 text-sm text-red-600">Erreur : {accessibiliteError}</div>
      )}

      {accessibiliteKpi?.reason === "no_loyer_data" && (
        <div className="mt-3 text-2xl font-bold text-blue-900">Pas de données</div>
      )}

      {!accessibiliteLoading &&
        !accessibiliteError &&
        selectedArrondissement !== "all" &&
        accessibiliteKpi?.m2_accessible !== undefined && (
          <div className="mt-3 text-2xl font-bold text-blue-900">
            {formatSqm(accessibiliteKpi.m2_accessible, 2)}
          </div>
      )}
    </div>
  );
}

export default KpiAccessibiliteCard;