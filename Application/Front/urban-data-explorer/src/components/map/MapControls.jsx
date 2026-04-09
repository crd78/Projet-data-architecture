function MapControls({ onReset }) {
    return (
        <div className="absolute left-3 top-3 z-10">
        <button type="button" onClick={onReset} className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-xs font-medium text-slate-700 shadow hover:bg-slate-50" >
        Recentrer
        </button>
        </div>
    );
}

export default MapControls;