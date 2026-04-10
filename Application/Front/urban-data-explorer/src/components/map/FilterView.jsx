import { useEffect, useState } from "react";

function FilterView({ onYearChange }) {
  const [year, setYear] = useState(2020);

  useEffect(() => {
    if (onYearChange) onYearChange(year);
  }, [year, onYearChange]);
  
  return (
    <aside className="lg:col-span-4 rounded-2xl border border-blue-100 bg-blue-50 shadow-sm">
      <div className="border-b border-blue-100 p-4">
        <h2 className="text-lg font-semibold text-blue-900">Metrics arrondissement</h2>
        <p className="text-sm text-blue-700/80">Filtres et indicateurs</p>
      </div>

      <div className="max-h-[75vh] overflow-y-auto p-4 space-y-4">
        <div className="rounded-lg border border-blue-100 bg-white p-3 text-slate-700">
          <p className="mb-2 text-sm font-medium text-slate-800">Année sélectionnée : {year}</p>

          <input
            type="range"
            min="2019"
            max="2021"
            step="1"
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
            className="w-full accent-blue-700"
          />

          <div className="mt-2 flex justify-between text-xs text-slate-500">
            <span>2019</span>
            <span>2020</span>
            <span>2021</span>
          </div>
        </div>

        <div className="rounded-lg border border-blue-100 bg-white p-3 text-slate-700">
          Bloc métrique 1
        </div>
        <div className="rounded-lg border border-blue-100 bg-white p-3 text-slate-700">
          Bloc métrique 2
        </div>
      </div>
    </aside>
  );
}

export default FilterView;