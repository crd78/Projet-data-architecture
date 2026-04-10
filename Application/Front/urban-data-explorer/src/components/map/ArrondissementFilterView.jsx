import { useMemo } from "react";
import useGeoJsonData from "../../hooks/useGeoJsonData";

function ArrondissementFilterView({ value, onChange }) {
  const { data } = useGeoJsonData("/data/communes.geojson");

  const options = useMemo(() => {
    if (!data?.features) return [];

    const map = new Map();
    for (const f of data.features) {
      const p = f?.properties || {};
      if (p.code && p.nom) map.set(p.code, p.nom);
    }

    return Array.from(map.entries())
      .map(([code, nom]) => ({ code, nom }))
      .sort((a, b) => a.code.localeCompare(b.code));
  }, [data]);

  return (
    <div className="rounded-xl border border-blue-100 bg-white/95 p-3 shadow-lg backdrop-blur">
      <label className="mb-2 block text-sm font-medium text-slate-800">
        Arrondissement
      </label>

      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full rounded-lg border border-blue-200 bg-white px-3 py-2 text-sm text-slate-800 outline-none focus:border-blue-500"
      >
        <option value="all">Tous les arrondissements</option>
        {options.map((opt) => (
          <option key={opt.code} value={opt.code}>
            {opt.nom}
          </option>
        ))}
      </select>
    </div>
  );
}

export default ArrondissementFilterView;