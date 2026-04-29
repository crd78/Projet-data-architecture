import { useEffect, useState } from "react";
import MapView from "../components/map/MapView";
import FilterView from "../components/map/MetricsView";
import YearFilterView from "../components/map/YearFilter";
import ArrondissementFilterView from "../components/map/ArrondissementFilterView";

const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000";

function geoCodeToArrNumber(code) {
  if (!code || code === "all") return null;
  const match = String(code).match(/(\d{2})$/);
  return match ? Number(match[1]) : null;
}

function DashboardPage() {
  const [selectedYear, setSelectedYear] = useState(2020);
  const [selectedArrondissement, setSelectedArrondissement] = useState("all");

  const [medianKpi, setMedianKpi] = useState(null);
  const [medianKpiLoading, setMedianKpiLoading] = useState(false);
  const [medianKpiError, setMedianKpiError] = useState("");
    const arrondissementNumber = geoCodeToArrNumber(selectedArrondissement);

  const handleArrondissementChange = (nextValue) => {
    setSelectedArrondissement(nextValue);
    console.log("Arrondissement sélectionné:", nextValue);
  };

  useEffect(() => {
    console.log("[KPI median_per_arrondissement] inputs", {
      apiBaseUrl: API_BASE_URL,
      selectedYear,
      selectedArrondissement,
      arrondissementNumber,
    });

    if (!arrondissementNumber) {
      console.log("[KPI median_per_arrondissement] skip (arrondissement=all)");
      setMedianKpi(null);
      setMedianKpiError("");
      setMedianKpiLoading(false);
      return;
    }

    const controller = new AbortController();

    async function load() {
      setMedianKpiLoading(true);
      setMedianKpiError("");

      const url = new URL("/kpi/median_price_per_arrondissement", API_BASE_URL);
      url.search = new URLSearchParams({
        annee: String(selectedYear),
        arrondissement: String(arrondissementNumber),
      }).toString();

      const res = await fetch(url.toString(), { signal: controller.signal });

      const payload = await res.json();

      if (!res.ok) throw new Error(payload?.detail || `HTTP ${res.status}`);

      setMedianKpi(payload);
    }

    load()
      .catch((err) => {
        if (err.name === "AbortError") return;
        setMedianKpiError(err.message || "Erreur inconnue");
        setMedianKpi(null);
      })
      .finally(() => setMedianKpiLoading(false));

    return () => controller.abort();
}, [selectedYear, selectedArrondissement, arrondissementNumber]);

  return (
    <main className="min-h-screen bg-slate-100">
      <header className="border-b border-slate-200 bg-white/80">
        <div className="mx-auto max-w-[1400px] px-4 py-4">
          <h1 className="text-2xl font-bold text-blue-900">Urban Data Explorer</h1>
          <p className="text-sm text-blue-600">Annee active : {selectedYear}</p>
        </div>
      </header>

      <div className="mx-auto max-w-[1600px] p-4">
        <div className="grid grid-cols-1 gap-4 lg:grid-cols-10">
          <section className="relative min-w-0 lg:col-span-6">
            <MapView
              geoJsonUrl="/data/communes.geojson"
              selectedArrondissement={selectedArrondissement}
            />

            <div className="pointer-events-none absolute right-4 top-4 z-30 w-[460px] max-w-[calc(100%-2rem)] space-y-3">
              <div className="pointer-events-auto">
                <YearFilterView year={selectedYear} onYearChange={setSelectedYear} />
              </div>
              <div className="pointer-events-auto">
                <ArrondissementFilterView
                  value={selectedArrondissement}
                  onChange={handleArrondissementChange}
                />
              </div>
            </div>
          </section>

          <aside className="lg:col-span-4">
            <FilterView
              selectedYear={selectedYear}
              selectedArrondissement={selectedArrondissement}
              arrondissementNumber={arrondissementNumber}
              medianKpi={medianKpi}
              medianKpiLoading={medianKpiLoading}
              medianKpiError={medianKpiError}
            />
          </aside>
        </div>
      </div>
    </main>
  );
}

export default DashboardPage;