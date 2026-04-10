import { useEffect, useState } from "react";

function FilterView({ onYearChange }) {
  const [year, setYear] = useState(2020);
  const [activeTab, setActiveTab] = useState("temporal");

  useEffect(() => {
    if (onYearChange) onYearChange(year);
  }, [year, onYearChange]);

  const tabButtonBase =
    "rounded-lg px-3 py-2 text-sm font-medium transition-colors";
  const tabActive = "bg-blue-700 text-white";
  const tabInactive = "bg-blue-100 text-blue-900 hover:bg-blue-200";

  return (
    <aside className="lg:col-span-4 rounded-2xl border border-blue-100 bg-blue-50 shadow-sm">
      <div className="border-b border-blue-100 p-4">

        <div className="mt-3 flex gap-2">
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

      <div className="max-h-[75vh] overflow-y-auto p-4 space-y-4">
        {activeTab === "temporal" && (
          <>
            <div className="rounded-lg border border-blue-100 bg-white p-3 text-slate-700">
              <p className="mb-2 text-sm font-medium text-slate-800">
                Année sélectionnée : {year}
              </p>

              <input
                type="range"
                min="2019"
                max="2023"
                step="1"
                value={year}
                onChange={(e) => setYear(Number(e.target.value))}
                className="w-full accent-blue-700"
              />

              <div className="mt-2 flex justify-between text-xs text-slate-500">
                <span>2019</span>
                <span>2020</span>
                <span>2021</span>
                <span>2022</span>
                <span>2023</span>
              </div>
            </div>

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