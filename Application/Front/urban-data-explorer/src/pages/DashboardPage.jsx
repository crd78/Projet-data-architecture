import MapView from "../components/map/MapView";
import FilterView from "../components/map/FilterView";
import { useState } from "react";

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
                <section className="min-w-0 lg:col-span-6">
                    <MapView geoJsonUrl="/data/communes.geojson" />
                </section>

                <FilterView onYearChange={setSelectedYear} />
            </div>
        </div>
    </main>
  );
}

export default DashboardPage;