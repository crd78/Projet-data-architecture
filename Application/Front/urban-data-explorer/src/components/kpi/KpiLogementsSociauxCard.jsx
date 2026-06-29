import { formatNumber } from "../../utils/formatters";

function KpiLogementsSociauxCard({
  logementsSociauxKpi,
  logementsSociauxLoading,
  logementsSociauxError
}) {
  return (
    <div className="rounded-lg border border-blue-100 bg-white p-3 text-slate-700">
      <div className="font-semibold">Logements sociaux financés</div>

      {logementsSociauxLoading && (
        <div className="mt-2 text-sm text-slate-500">Chargement…</div>
      )}

      {!!logementsSociauxError && (
        <div className="mt-2 text-sm text-red-600">Erreur : {logementsSociauxError}</div>
      )}

      {!logementsSociauxLoading &&
        !logementsSociauxError &&
        logementsSociauxKpi?.logements_sociaux_finances_total !== undefined && (
          <div className="mt-3 text-2xl font-bold text-blue-900">
            {formatNumber(logementsSociauxKpi.logements_sociaux_finances_total, 0)}
          </div>
      )}
    </div>
  );
}

export default KpiLogementsSociauxCard;