import MapView from "../components/map/MapView";

function DashboardPage() {
  return (
    <main className="min-h-screen bg-slate-100">
        <header className="border-b border-slate-200 bg-white/80">
            <div className="mx-auto max-w-[1400px] px-4 py-4">
                <h1 className="text-2xl font-bold text-slate-900">Urban Data Explorer</h1>
            </div>
        </header>

        <div className="mx-auto max-w-[1600px] p-4">
            <div className="grid grid-cols-1 gap-4 lg:grid-cols-10">
                <section className="min-w-0 lg:col-span-6">
                    <MapView geoJsonUrl="/data/communes.geojson" />
                </section>

                <aside className="lg:col-span-4 rounded-2xl border border-slate-200 bg-white shadow-sm">
                    <div className="border-b border-slate-200 p-4">
                        <h2 className="text-lg font-semibold text-slate-900">Metrics arrondissement</h2>
                        <p className="text-sm text-slate-600">Filtres et indicateurs</p>
                    </div>

                    <div className="max-h-[75vh] overflow-y-auto p-4 space-y-4">
                        <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
                            Bloc menu de sélection
                        </div>
                        <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
                            Bloc métrique 1
                        </div>
                        <div className="rounded-lg border border-slate-100 bg-slate-50 p-3">
                            Bloc métrique 2
                        </div>
                    </div>
                </aside>
            </div>
        </div>
    </main>
  );
}

export default DashboardPage;