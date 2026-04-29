const YEARS = [2019, 2020, 2021, 2022, 2023];

function YearFilterView({ year, onYearChange }) {
  return (
    <div>
      <div className="mb-3 flex items-center justify-between gap-4">
        <label
          htmlFor="year-filter"
          className="text-[11px] font-bold uppercase tracking-[0.14em] text-[#77767e]"
        >
          Millésime
        </label>
        <span className="rounded-full bg-[#1a1f36] px-3 py-1 font-['Space_Grotesk'] text-xs font-medium text-white">
          {year}
        </span>
      </div>

      <input
        id="year-filter"
        type="range"
        min="2019"
        max="2023"
        step="1"
        value={year}
        onChange={(e) => onYearChange(Number(e.target.value))}
        className="urban-range w-full"
      />

      <div className="mt-2 grid grid-cols-5 text-center font-['Space_Grotesk'] text-[10px] font-medium text-[#77767e]">
        {YEARS.map((item) => (
          <button
            key={item}
            type="button"
            onClick={() => onYearChange(item)}
            className={`rounded-md px-1 py-1 transition hover:bg-white/70 ${
              item === year ? "text-[#03071d]" : ""
            }`}
          >
            {item}
          </button>
        ))}
      </div>
    </div>
  );
}

export default YearFilterView;
