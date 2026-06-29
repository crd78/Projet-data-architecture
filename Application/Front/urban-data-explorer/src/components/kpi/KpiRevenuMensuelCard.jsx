import { formatEuro } from "../../utils/formatters";

function KpiRevenuMensuelCard({
  selectedArrondissement,
  accessibiliteKpi,
  accessibiliteLoading,
  accessibiliteError
}) {
  return (
    <div className="rounded-lg border border-blue-100 bg-white p-3 text-slate-700">
      <div className="font-semibold">Revenu médian mensuel</div>

      {selectedArrondissement === "all" && (
        <div className="mt-2 text-sm text-slate-500">
          Sélectionne un arrondissement pour afficher la KPI.
        </div>
      )}

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
        accessibiliteKpi?.income_monthly !== undefined && (
          <div className="mt-3 text-2xl font-bold text-blue-900">
            {formatEuro(accessibiliteKpi.income_monthly, 0)}
          </div>
      )}
    </div>
  );
}

export default KpiRevenuMensuelCard;