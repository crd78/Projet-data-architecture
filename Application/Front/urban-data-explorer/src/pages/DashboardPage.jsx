import MapView from "../components/map/MapView";

function DashboardPage() {
return (
    <main className="min-h-screen bg-slate-100">
        <header className="border-b border-slate-200 bg-white/80">
        <div className="mx-auto max-w-7xl px-4 py-4">
            <h1 className="text-2xl font-bold text-slate-900">Urban Data Explorer</h1>
        </div>
        </header>

        <div className="mx-auto max-w-7xl p-4">
            <MapView geoJsonUrl="/data/communes.geojson" />
        </div>
    </main>
);
}

export default DashboardPage;