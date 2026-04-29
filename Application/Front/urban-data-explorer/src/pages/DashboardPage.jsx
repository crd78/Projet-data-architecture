import { useState } from "react";
import useMedianKpi from "../hooks/useMedianKpi";
import useRepartitionKpi from "../hooks/useRepartitionKpi";
import useLogementsSociauxKpi from "../hooks/useLogementsSociauxKpi";
import useAccessibiliteKpi from "../hooks/useAccessibiliteKpi";
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
  const [selectedArrondissementB, setSelectedArrondissementB] = useState("all");
  const [revenuProportion, setRevenuProportion] = useState(0.4);

  const arrondissementNumber = geoCodeToArrNumber(selectedArrondissement);
  const arrondissementNumberB = geoCodeToArrNumber(selectedArrondissementB);

  // Prix median location/achat (A)
  const { data: medianLocation, loading: medianLocationLoading, error: medianLocationError } =
    useMedianKpi(selectedYear, arrondissementNumber, "location");
  const { data: medianAchat, loading: medianAchatLoading, error: medianAchatError } =
    useMedianKpi(selectedYear, arrondissementNumber, "achat");

  // Prix median location/achat (B)
  const { data: medianLocationB, loading: medianLocationLoadingB, error: medianLocationErrorB } =
    useMedianKpi(selectedYear, arrondissementNumberB, "location");
  const { data: medianAchatB, loading: medianAchatLoadingB, error: medianAchatErrorB } =
    useMedianKpi(selectedYear, arrondissementNumberB, "achat");

  // Repartition (A/B)
  const { data: repartitionKpi, loading: repartitionLoading, error: repartitionError } =
    useRepartitionKpi(selectedYear, arrondissementNumber);
  const { data: repartitionKpiB, loading: repartitionLoadingB, error: repartitionErrorB } =
    useRepartitionKpi(selectedYear, arrondissementNumberB);

  // Logements sociaux (A/B)
  const { data: logementsSociauxKpi, loading: logementsSociauxLoading, error: logementsSociauxError } =
    useLogementsSociauxKpi(selectedYear, arrondissementNumber);
  const { data: logementsSociauxKpiB, loading: logementsSociauxLoadingB, error: logementsSociauxErrorB } =
    useLogementsSociauxKpi(selectedYear, arrondissementNumberB);

  // Accessibilite (A/B)
  const { data: accessibiliteKpi, loading: accessibiliteLoading, error: accessibiliteError } =
    useAccessibiliteKpi(selectedYear, arrondissementNumber, revenuProportion);
  const { data: accessibiliteKpiB, loading: accessibiliteLoadingB, error: accessibiliteErrorB } =
    useAccessibiliteKpi(selectedYear, arrondissementNumberB, revenuProportion);

  const handleArrondissementChange = (nextValue) => {
    setSelectedArrondissement(nextValue);
  };

  const handleArrondissementChangeB = (nextValue) => {
    setSelectedArrondissementB(nextValue);
  };

  return (
    <main className="min-h-screen bg-slate-100">
      <header className="border-b border-slate-200 bg-white/80">
        <div className="mx-auto max-w-[1400px] px-4 py-4">
          <h1 className="text-2xl font-bold text-blue-900">Urban Data Explorer</h1>
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
              selectedArrondissementB={selectedArrondissementB}
              onArrondissementBChange={handleArrondissementChangeB}
              revenuProportion={revenuProportion}
              onRevenuProportionChange={setRevenuProportion}

              medianLocation={medianLocation}
              medianLocationLoading={medianLocationLoading}
              medianLocationError={medianLocationError}
              medianAchat={medianAchat}
              medianAchatLoading={medianAchatLoading}
              medianAchatError={medianAchatError}

              medianLocationB={medianLocationB}
              medianLocationLoadingB={medianLocationLoadingB}
              medianLocationErrorB={medianLocationErrorB}
              medianAchatB={medianAchatB}
              medianAchatLoadingB={medianAchatLoadingB}
              medianAchatErrorB={medianAchatErrorB}

              repartitionKpi={repartitionKpi}
              repartitionLoading={repartitionLoading}
              repartitionError={repartitionError}
              repartitionKpiB={repartitionKpiB}
              repartitionLoadingB={repartitionLoadingB}
              repartitionErrorB={repartitionErrorB}

              logementsSociauxKpi={logementsSociauxKpi}
              logementsSociauxLoading={logementsSociauxLoading}
              logementsSociauxError={logementsSociauxError}
              logementsSociauxKpiB={logementsSociauxKpiB}
              logementsSociauxLoadingB={logementsSociauxLoadingB}
              logementsSociauxErrorB={logementsSociauxErrorB}

              accessibiliteKpi={accessibiliteKpi}
              accessibiliteLoading={accessibiliteLoading}
              accessibiliteError={accessibiliteError}
              accessibiliteKpiB={accessibiliteKpiB}
              accessibiliteLoadingB={accessibiliteLoadingB}
              accessibiliteErrorB={accessibiliteErrorB}
            />
          </aside>
        </div>
      </div>
    </main>
  );
}

export default DashboardPage;