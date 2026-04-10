import { useState } from "react";

function FilterView() {
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
              Metrics 1 : Prix médian au mètre carré
            </div>
            <div className="rounded-lg border border-blue-100 bg-white p-3 text-slate-700">
              Metrics 2 : Répartition du parc immobilier
            </div>
            <div className="rounded-lg border border-blue-100 bg-white p-3 text-slate-700">
              Metrics 3 : Part des logements sociaux
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