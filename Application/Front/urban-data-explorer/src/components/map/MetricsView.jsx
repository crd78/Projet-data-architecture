import { useState } from "react";

function FilterView({
  selectedYear,
  selectedArrondissement,
  arrondissementNumber,
  medianLocation,
  medianLocationLoading,
  medianLocationError,
  medianAchat,
  medianAchatLoading,
  medianAchatError,
  repartitionKpi,
  repartitionLoading,
  repartitionError,
  logementsSociauxKpi,
  logementsSociauxLoading,
  logementsSociauxError,
}) {
  const [activeTab, setActiveTab] = useState("temporal");

  const tabButtonBase = "rounded-xl px-5 py-2.5 text-base font-semibold transition-colors";
  const tabActive = "bg-blue-700 text-white";
  const tabInactive = "bg-blue-100 text-blue-900 hover:bg-blue-200";

  return (
    <aside className="h-full rounded-2xl border border-blue-100 bg-blue-50 shadow-sm flex flex-col">
      <div className="border-b border-blue-100 p-4">
        <div className="mt-1 flex gap-2">
          <button
            type="button"
            onClick={() => setActiveTab("temporal")}
            className={`${tabButtonBase} ${activeTab === "temporal" ? tabActive : tabInactive}`}
          >
            KPI temporels
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("other")}
            className={`${tabButtonBase} ${activeTab === "other" ? tabActive : tabInactive}`}
          >
            Autres KPI
          </button>
        </div>
      </div>

      <div className="max-h-[55vh] overflow-y-auto p-4 space-y-4">
        {activeTab === "temporal" && (
          <>
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
                    {!medianLocationLoading &&
                      !medianLocationError && (
                        <div className="text-2xl font-bold text-blue-900">
                          {medianLocation?.median_price_loyer ?? "—"}
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
                    {!medianAchatLoading &&
                      !medianAchatError && (
                        <div className="text-2xl font-bold text-blue-900">
                          {medianAchat?.median_price_achat ?? "—"}
                        </div>
                    )}
                  </div>
                </div>
              )}
            </div>

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
                          <span>{item.percentage}%</span>
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
                    {logementsSociauxKpi.logements_sociaux_finances_total}
                  </div>
              )}
            </div>

            <div className="rounded-lg border border-blue-100 bg-white p-3 text-slate-700">
              Metrics 4 : Score de nuisance sonore
            </div>
            <div className="rounded-lg border border-blue-100 bg-white p-3 text-slate-700">
              Metrics 5 : Accessibilité 
            </div>
          </>
        )}

        {activeTab === "other" && (
          <>
            <div className="rounded-lg border border-blue-100 bg-white p-3 text-slate-700">
              Metrics 1 : Disponibilité des stationnements
            </div>
            <div className="rounded-lg border border-blue-100 bg-white p-3 text-slate-700">
              Metrics 2 : Activité dans le quartier
            </div>
            <div className="rounded-lg border border-blue-100 bg-white p-3 text-slate-700">
              Metrics 3 : Temps moyen de résolution des signalements
            </div>
          </>
        )}
      </div>
    </aside>
  );
}

export default FilterView;