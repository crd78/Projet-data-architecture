import { useMemo, useState } from "react";
import useMedianKpi from "../hooks/useMedianKpi";
import useRepartitionKpi from "../hooks/useRepartitionKpi";
import MapView from "../components/map/MapView";
import FilterView from "../components/map/MetricsView";
import YearFilterView from "../components/map/YearFilter";
import ArrondissementFilterView from "../components/map/ArrondissementFilterView";
import useLogementsSociauxKpi from "../hooks/useLogementsSociauxKpi";

function geoCodeToArrNumber(code) {
  if (!code || code === "all") return null;
  const match = String(code).match(/(\d{2})$/);
  return match ? Number(match[1]) : null;
}

function formatArrondissementLabel(code, arrondissementNumber) {
  if (!code || code === "all") return "Paris intra-muros";
  if (!arrondissementNumber) return "Arrondissement sélectionné";

  return arrondissementNumber === 1
    ? "Paris 1er arrondissement"
    : `Paris ${arrondissementNumber}e arrondissement`;
}

function DashboardPage() {
  const [selectedYear, setSelectedYear] = useState(2020);
  const [selectedArrondissement, setSelectedArrondissement] = useState("all");

  const arrondissementNumber = geoCodeToArrNumber(selectedArrondissement);
  const districtLabel = useMemo(
    () => formatArrondissementLabel(selectedArrondissement, arrondissementNumber),
    [selectedArrondissement, arrondissementNumber]
  );

  const { data: medianKpi, loading: medianKpiLoading, error: medianKpiError } =
    useMedianKpi(selectedYear, arrondissementNumber);

  const { data: repartitionKpi, loading: repartitionLoading, error: repartitionError } =
    useRepartitionKpi(selectedYear, arrondissementNumber);

  const { data: logementsSociauxKpi, loading: logementsSociauxLoading, error: logementsSociauxError } =
    useLogementsSociauxKpi(selectedYear, arrondissementNumber);

  const handleArrondissementChange = (nextValue) => {
    setSelectedArrondissement(nextValue);
  };

  return (
    <main className="flex h-screen flex-col overflow-hidden bg-[#f7f9fb] font-['Inter'] text-[#191c1e]">
      <header className="z-40 flex h-16 shrink-0 items-center justify-between border-b border-white/10 bg-[#1a1f36] px-4 text-white shadow-[0_16px_40px_-24px_rgba(3,7,29,0.65)] sm:px-6">
        <div className="flex min-w-0 items-center gap-4">
          <div className="grid h-10 w-10 shrink-0 place-items-center rounded-lg border border-white/15 bg-white/10">
            <svg aria-hidden="true" className="h-5 w-5" viewBox="0 0 24 24" fill="none">
              <path
                d="M4 7.5 9 5l6 2.5 5-2.5v11.5l-5 2.5-6-2.5-5 2.5V7.5Z"
                stroke="currentColor"
                strokeLinejoin="round"
                strokeWidth="1.8"
              />
              <path d="M9 5v11.5M15 7.5V19" stroke="currentColor" strokeWidth="1.8" />
            </svg>
          </div>

          <div className="min-w-0">
            <p className="text-[10px] font-bold uppercase tracking-[0.18em] text-[#8286a2]">
              Urban Intel: Paris
            </p>
            <h1 className="truncate text-[22px] font-semibold leading-none tracking-normal sm:text-[24px]">
              Urban Data Explorer
            </h1>
          </div>

          <nav className="hidden items-center gap-1 border-l border-white/10 pl-4 lg:flex">
            {["Carte", "KPI", "Territoire"].map((item, index) => (
              <span
                key={item}
                className={`rounded-lg px-3 py-2 text-sm font-semibold transition ${
                  index === 0
                    ? "bg-white/15 text-white"
                    : "text-[#c1c5e3] hover:bg-white/10 hover:text-white"
                }`}
              >
                {item}
              </span>
            ))}
          </nav>
        </div>

        <div className="flex items-center gap-3">
          <div className="hidden items-center gap-2 rounded-full border border-white/10 bg-white/8 px-3 py-1.5 text-xs font-semibold text-[#c1c5e3] md:flex">
            <span className="h-2 w-2 rounded-full bg-[#10b981] shadow-[0_0_0_4px_rgba(16,185,129,0.18)]" />
            Flux Open Data actif
          </div>
          <div className="rounded-lg border border-white/10 bg-white/8 px-3 py-2 font-['Space_Grotesk'] text-xs font-medium text-white">
            {selectedYear}
          </div>
        </div>
      </header>

      <div className="grid min-h-0 flex-1 grid-cols-1 grid-rows-[minmax(0,58vh)_minmax(0,1fr)] overflow-hidden lg:grid-cols-[minmax(0,1fr)_380px] lg:grid-rows-1">
        <section className="relative min-h-0 overflow-hidden bg-[#e6e8ea]">
          <MapView
            geoJsonUrl="/data/communes.geojson"
            selectedArrondissement={selectedArrondissement}
            onArrondissementSelect={handleArrondissementChange}
          />

          <div className="pointer-events-none absolute left-4 top-4 z-30 flex w-[min(22rem,calc(100vw-2rem))] flex-col gap-4 sm:left-6 sm:top-6">
            <div className="glass-panel pointer-events-auto overflow-hidden rounded-[24px] p-4">
              <div className="inner-sheen" />
              <p className="mb-3 text-[11px] font-bold uppercase tracking-[0.16em] text-[#46464d]">
                Pilotage spatial
              </p>
              <div className="space-y-4">
                <ArrondissementFilterView
                  value={selectedArrondissement}
                  onChange={handleArrondissementChange}
                />
                <YearFilterView year={selectedYear} onYearChange={setSelectedYear} />
              </div>
            </div>
          </div>

          <div className="pointer-events-none absolute bottom-4 left-4 z-30 hidden sm:bottom-6 sm:left-6 sm:block">
            <div className="pointer-events-auto w-72 rounded-[24px] border border-[#e0e3e5] bg-white p-5 shadow-[0_10px_25px_-5px_rgba(26,31,54,0.14)]">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-[#77767e]">
                    Vue active
                  </p>
                  <h2 className="mt-2 text-[22px] font-semibold leading-tight tracking-normal text-[#1a1f36]">
                    {districtLabel}
                  </h2>
                </div>
                <span className="rounded-full bg-[#dde1ff] px-3 py-1 font-['Space_Grotesk'] text-xs font-medium text-[#001f4b]">
                  {selectedArrondissement === "all" ? "20 zones" : `PAR-${arrondissementNumber}`}
                </span>
              </div>

              <div className="mt-4 grid grid-cols-3 gap-2 border-t border-[#e0e3e5] pt-4">
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-[#77767e]">
                    Année
                  </p>
                  <p className="mt-1 font-['Space_Grotesk'] text-sm font-medium text-[#03071d]">
                    {selectedYear}
                  </p>
                </div>
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-[#77767e]">
                    Couche
                  </p>
                  <p className="mt-1 font-['Space_Grotesk'] text-sm font-medium text-[#03071d]">
                    Commune
                  </p>
                </div>
                <div>
                  <p className="text-[10px] font-bold uppercase tracking-[0.12em] text-[#77767e]">
                    Signal
                  </p>
                  <p className="mt-1 font-['Space_Grotesk'] text-sm font-medium text-[#006c49]">
                    Actif
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <aside className="urban-scrollbar z-20 min-h-0 overflow-y-auto border-t border-[#c7c5ce] bg-white shadow-[-18px_0_40px_-34px_rgba(3,7,29,0.7)] lg:border-l lg:border-t-0">
          <div className="sticky top-0 z-10 border-b border-[#e0e3e5] bg-white/92 px-6 py-5 backdrop-blur-xl">
            <p className="text-[11px] font-bold uppercase tracking-[0.16em] text-[#77767e]">
              Deep Intelligence
            </p>
            <h2 className="mt-2 text-[24px] font-semibold leading-tight tracking-normal text-[#03071d]">
              {districtLabel}
            </h2>
            <div className="mt-4 h-1 w-14 rounded-full bg-[#3b82f6]" />
          </div>

          <div className="space-y-6 p-6">
            <FilterView
              selectedYear={selectedYear}
              selectedArrondissement={selectedArrondissement}
              arrondissementNumber={arrondissementNumber}
              districtLabel={districtLabel}
              medianKpi={medianKpi}
              medianKpiLoading={medianKpiLoading}
              medianKpiError={medianKpiError}
              repartitionKpi={repartitionKpi}
              repartitionLoading={repartitionLoading}
              repartitionError={repartitionError}
              logementsSociauxKpi={logementsSociauxKpi}
              logementsSociauxLoading={logementsSociauxLoading}
              logementsSociauxError={logementsSociauxError}
            />

            <div className="rounded-lg border border-[#e0e3e5] bg-[#f2f4f6] p-4">
              <div className="mb-3 flex items-center justify-between">
                <h3 className="text-[11px] font-bold uppercase tracking-[0.16em] text-[#46464d]">
                  Légende carte
                </h3>
                <span className="font-['Space_Grotesk'] text-xs font-medium text-[#3b82f6]">
                  Deck.gl
                </span>
              </div>
              <div className="space-y-3 text-sm text-[#46464d]">
                <div className="flex items-center gap-3 rounded-lg bg-white/70 px-3 py-2">
                  <span className="h-3 w-3 rounded-full bg-[#10b981] ring-2 ring-white" />
                  Arrondissement sélectionné
                </div>
                <div className="flex items-center gap-3 rounded-lg bg-white/70 px-3 py-2">
                  <span className="h-3 w-3 rounded-full bg-[#3b82f6] ring-2 ring-white" />
                  Réseau viaire au zoom rapproché
                </div>
              </div>
            </div>

            <div className="rounded-lg border border-[#e0e3e5] bg-white p-4 text-xs leading-5 text-[#46464d] shadow-[0_10px_25px_-18px_rgba(26,31,54,0.2)]">
              <div className="mb-2 flex items-center justify-between font-bold uppercase tracking-[0.12em]">
                <span>Synchronisation</span>
                <span className="text-[#006c49]">Active</span>
              </div>
              Les indicateurs sont préparés pour les flux KPI. Le loyer médian se met à jour
              selon l'année et l'arrondissement sélectionnés.
            </div>
          </div>
        </aside>
      </div>
    </main>
  );
}

export default DashboardPage;
