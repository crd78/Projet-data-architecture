import { useMemo } from "react";
import useGeoJsonData from "../../hooks/useGeoJsonData";

function ArrondissementFilterView({ value, onChange }) {
  const { data, loading, error } = useGeoJsonData("/data/communes.geojson");

  const options = useMemo(() => {
    if (!data?.features) return [];

    const map = new Map();
    for (const feature of data.features) {
      const properties = feature?.properties || {};
      if (properties.code && properties.nom) map.set(properties.code, properties.nom);
    }

    return Array.from(map.entries())
      .map(([code, nom]) => ({ code, nom }))
      .sort((a, b) => a.code.localeCompare(b.code));
  }, [data]);

  return (
    <div>
      <div className="mb-2 flex items-center justify-between gap-4">
        <label
          htmlFor="arrondissement-filter"
          className="text-[11px] font-bold uppercase tracking-[0.14em] text-[#77767e]"
        >
          Arrondissement
        </label>
        <span className="font-['Space_Grotesk'] text-[11px] font-medium text-[#3b82f6]">
          {loading ? "..." : `${options.length || 20} zones`}
        </span>
      </div>

      <select
        id="arrondissement-filter"
        value={value}
        onChange={(event) => onChange(event.target.value)}
        disabled={loading || !!error}
        className="w-full rounded-lg border border-[#c7c5ce] bg-white/90 px-3 py-2.5 text-sm font-semibold text-[#1a1f36] outline-none transition focus:border-[#3b82f6] focus:ring-4 focus:ring-[#3b82f6]/15 disabled:cursor-not-allowed disabled:opacity-70"
      >
        <option value="all">Tous les arrondissements</option>
        {options.map((option) => (
          <option key={option.code} value={option.code}>
            {option.nom}
          </option>
        ))}
      </select>

      {error && (
        <p className="mt-2 rounded-lg bg-[#ffdad6] px-3 py-2 text-xs font-semibold text-[#93000a]">
          {error}
        </p>
      )}
    </div>
  );
}

export default ArrondissementFilterView;
