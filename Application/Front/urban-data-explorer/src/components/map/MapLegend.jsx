function MapLegend({ loading, error, featureCount }) {
    return (
        <aside className="absolute right-3 top-3 z-10 w-72 rounded-xl border border-slate-200 bg-white/95 p-3 shadow-lg">
        <h2 className="mb-2 text-sm font-semibold text-slate-900">Informations</h2>
        <div className="space-y-1 text-xs text-slate-700">
        <p><span className="font-medium">Features:</span> {featureCount}</p>
        <p><span className="font-medium">Statut:</span> {loading ? "Chargement..." : error ? "Erreur" : "Pret"}</p>
        {error ? <p className="text-red-600">{error}</p> : null}
        </div>
        </aside>
    );
}

export default MapLegend;