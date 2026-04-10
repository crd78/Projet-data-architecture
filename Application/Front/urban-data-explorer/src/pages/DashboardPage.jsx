import { useState } from "react";
import MapView from "../components/map/MapView";
import FilterView from "../components/map/FilterView";
import YearFilterView from "../components/map/MetricsView";

function DashboardPage() {
  const [selectedYear, setSelectedYear] = useState(2020);

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
                    <MapView geoJsonUrl="/data/communes.geojson" />
                    <div className="pointer-events-none absolute right-4 top-4 z-30 w-[460px] max-w-[calc(100%-2rem)]">
                        <div className="pointer-events-auto">
                            <YearFilterView year={selectedYear} onYearChange={setSelectedYear} />
                        </div>
                    </div>
                </section>

                <aside className="lg:col-span-4">
                    <FilterView />
                </aside>
            </div>
        </div>
    </main>
  );
}

export default DashboardPage;