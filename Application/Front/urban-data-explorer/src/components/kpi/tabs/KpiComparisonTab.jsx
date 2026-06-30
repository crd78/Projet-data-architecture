import ArrondissementFilterView from "../../map/ArrondissementFilterView";
import ComparisonCard from "../ComparisonCard";
import {
  formatEuro,
  formatNumber,
  formatPercent,
  formatSqm
} from "../../../utils/formatters";

function formatAchat(value) {
  if (value === null || value === undefined) return "—";
  return Number(value);
}

function KpiComparisonTab({
  selectedArrondissement,
  selectedArrondissementB,
  onArrondissementBChange,
  revenuProportion,
  onRevenuProportionChange,

  medianLocation,
  medianAchat,
  medianLocationB,
  medianAchatB,

  repartitionKpi,
  repartitionKpiB,

  logementsSociauxKpi,
  logementsSociauxKpiB,

  accessibiliteKpi,
  accessibiliteKpiB,
}) {
  return (
    <>
      <div className="rounded-lg border border-blue-100 bg-white p-3 text-slate-700 space-y-3">
        <div className="font-semibold">Comparer deux arrondissements</div>
        <div className="grid grid-cols-2 gap-3">
          <ArrondissementFilterView value={selectedArrondissement} onChange={() => {}} />
          <ArrondissementFilterView value={selectedArrondissementB} onChange={onArrondissementBChange} />
        </div>
      </div>

      <ComparisonCard
        title="Prix au m2 (location mediane / achat moyen)"
        left={
          <div className="text-lg font-bold text-blue-900">
            {formatNumber(medianLocation?.median_price_loyer, 2)} / {formatNumber(formatAchat(medianAchat?.median_price_achat), 2)}
          </div>
        }
        right={
          <div className="text-lg font-bold text-blue-900">
            {formatNumber(medianLocationB?.median_price_loyer, 2)} / {formatNumber(formatAchat(medianAchatB?.median_price_achat), 2)}
          </div>
        }
      />

      <ComparisonCard
        title="Répartition du parc immobilier"
        left={
          Array.isArray(repartitionKpi?.logements_repartition) &&
          repartitionKpi.logements_repartition.map((item) => (
            <div key={`a-${item.type}`} className="space-y-1">
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
          ))
        }
        right={
          Array.isArray(repartitionKpiB?.logements_repartition) &&
          repartitionKpiB.logements_repartition.map((item) => (
            <div key={`b-${item.type}`} className="space-y-1">
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
          ))
        }
      />

      <ComparisonCard
        title="Logements sociaux financés"
        left={
          <div className="text-2xl font-bold text-blue-900">
            {formatNumber(logementsSociauxKpi?.logements_sociaux_finances_total, 0)}
          </div>
        }
        right={
          <div className="text-2xl font-bold text-blue-900">
            {formatNumber(logementsSociauxKpiB?.logements_sociaux_finances_total, 0)}
          </div>
        }
      />

      <ComparisonCard
        title="Revenu médian mensuel"
        left={
          <div className="text-2xl font-bold text-blue-900">
            {formatEuro(accessibiliteKpi?.income_monthly, 0)}
          </div>
        }
        right={
          <div className="text-2xl font-bold text-blue-900">
            {formatEuro(accessibiliteKpiB?.income_monthly, 0)}
          </div>
        }
      />

      <div className="rounded-lg border border-blue-100 bg-white p-3 text-slate-700">
        <div className="font-semibold">Accessibilité (m² louables)</div>
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
        <div className="mt-3 grid grid-cols-2 gap-4">
          <div className="text-2xl font-bold text-blue-900">
            {formatSqm(accessibiliteKpi?.m2_accessible, 2)}
          </div>
          <div className="text-2xl font-bold text-blue-900">
            {formatSqm(accessibiliteKpiB?.m2_accessible, 2)}
          </div>
        </div>
      </div>
    </>
  );
}

export default KpiComparisonTab;
