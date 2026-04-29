import { useState } from "react";
import useMedianKpi from "../hooks/useMedianKpi";
import MapView from "../components/map/MapView";
import FilterView from "../components/map/MetricsView";
import YearFilterView from "../components/map/YearFilter";
import ArrondissementFilterView from "../components/map/ArrondissementFilterView";

function geoCodeToArrNumber(code) {
  if (!code || code === "all") return null;
  const match = String(code).match(/(\d{2})$/);
  return match ? Number(match[1]) : null;
}

function DashboardPage() {
  const [selectedYear, setSelectedYear] = useState(2020);
  const [selectedArrondissement, setSelectedArrondissement] = useState("all");
  
  const arrondissementNumber = geoCodeToArrNumber(selectedArrondissement);
  
  const { data: medianKpi, loading: medianKpiLoading, error: medianKpiError } =
    useMedianKpi(selectedYear, arrondissementNumber);

  const handleArrondissementChange = (nextValue) => {
    setSelectedArrondissement(nextValue);
    console.log("Arrondissement sélectionné:", nextValue);
  };

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