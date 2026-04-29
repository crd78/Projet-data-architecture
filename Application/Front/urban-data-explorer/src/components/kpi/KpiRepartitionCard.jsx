import { formatPercent } from "../../utils/formatters";

function KpiRepartitionCard({
  selectedArrondissement,
  repartitionKpi,
  repartitionLoading,
  repartitionError
}) {
  return (
    <div className="rounded-lg border border-blue-100 bg-white p-3 text-slate-700">
      <div className="font-semibold">Répartition du parc immobilier</div>

      {selectedArrondissement === "all" && (
        <div className="mt-2 text-sm text-slate-500">
          Sélectionne un arrondissement pour afficher la répartition.
        </div>
      )}

      {repartitionLoading && (
        <div className="mt-2 text-sm text-slate-500">Chargement…</div>
      )}

      {!!repartitionError && (
        <div className="mt-2 text-sm text-red-600">Erreur : {repartitionError}</div>
      )}

      {!repartitionLoading &&
        !repartitionError &&
        selectedArrondissement !== "all" &&
        Array.isArray(repartitionKpi?.logements_repartition) &&
        repartitionKpi.logements_repartition.length === 0 && (
          <div className="mt-3 text-2xl font-bold text-blue-900">Pas de données</div>
      )}

      {Array.isArray(repartitionKpi?.logements_repartition) &&
        repartitionKpi.logements_repartition.length > 0 && (
          <div className="mt-3 space-y-2">
            {repartitionKpi.logements_repartition.map((item) => (
              <div key={item.type} className="space-y-1">
                <div className="flex justify-between text-xs text-slate-600">
                  <span>{item.type}</span>
                  <span>{formatPercent(item.percentage, 0)}</span>
                </div>
                <div className="h-2 w-full rounded bg-slate-100">
                  <div
                    className="h-2 rounded bg-blue-600"
                    style={{ width: `${item.percentage}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
      )}
    </div>
  );
}

export default KpiRepartitionCard;