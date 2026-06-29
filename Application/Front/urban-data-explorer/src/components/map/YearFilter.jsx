function YearFilterView({ year, onYearChange }) {
  return (
    <div className="rounded-xl border border-blue-100 bg-white/95 p-3 shadow-lg backdrop-blur">
      <input
        type="range"
        min="2019"
        max="2023"
        step="1"
        value={year}
        onChange={(e) => onYearChange(Number(e.target.value))}
        className="w-full accent-blue-700"
      />

      <div className="mt-2 flex justify-between text-xs text-slate-500">
        <span>2019</span>
        <span>2020</span>
        <span>2021</span>
        <span>2022</span>
        <span>2023</span>
      </div>
    </div>
  );
}

export default YearFilterView;