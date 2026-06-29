import { useState } from "react";
import useMedianKpi from "../hooks/useMedianKpi";
import useRepartitionKpi from "../hooks/useRepartitionKpi";
import useLogementsSociauxKpi from "../hooks/useLogementsSociauxKpi";
import useAccessibiliteKpi from "../hooks/useAccessibiliteKpi";
import MapView from "../components/map/MapView";
import FilterView from "../components/map/MetricsView";
import YearFilterView from "../components/map/YearFilter";
import ArrondissementFilterView from "../components/map/ArrondissementFilterView";
import useDisponibiliteStationnement from "../hooks/useDisponibiliteStationnement";
import useActiviteQuartier from "../hooks/useActiviteQuartier";
import usePropreteGenerale from "../hooks/usePropreteGenerale";
import useNuisanceSonore from "../hooks/useNuisanceSonore";

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
  const [clickedPosition, setClickedPosition] = useState(null);

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

  // Score stationnement
  const {
    data: disponibiliteStationnementKpi,
    loading: disponibiliteStationnementLoading,
    error: disponibiliteStationnementError,
  } = useDisponibiliteStationnement(clickedPosition);

  // Score activité dans le quartier
  const {
    data: activiteQuartierKpi,
    loading: activiteQuartierLoading,
    error: activiteQuartierError,
  } = useActiviteQuartier(clickedPosition);

  // Score propreté générale
  const {
    data: propreteGeneraleKpi,
    loading: propreteGeneraleLoading,
    error: propreteGeneraleError,
  } = usePropreteGenerale(clickedPosition);

  // Score nuisance sonore
  const {
    data: nuisanceSonoreKpi,
    loading: nuisanceSonoreLoading,
    error: nuisanceSonoreError,
  } = useNuisanceSonore(clickedPosition);

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
              onMapClick={setClickedPosition}
              onSelectArrondissement={setSelectedArrondissement}
            />
            <div className="pointer-events-none absolute bottom-4 right-4 z-30 w-[360px] max-w-[calc(100%-2rem)]">
              <div className="pointer-events-auto rounded-2xl border border-blue-100/60 bg-white/60 p-4 shadow-lg backdrop-blur-sm">
                <div className="text-sm font-semibold text-blue-900">
                  Informations autour du point
                </div>

                {!clickedPosition && (
                  <div className="mt-2 text-sm text-slate-500">
                    Clique sur la carte pour calculer les KPI.
                  </div>
                )}

                {clickedPosition && (
                  <div className="mt-4 border-t border-blue-100 pt-3">
                    <div className="text-xs font-medium text-slate-600">Score disponibilité stationnement /100</div>
                    {disponibiliteStationnementLoading && (
                      <div className="mt-2 text-sm text-slate-500">Chargement…</div>
                    )}
                    {!!disponibiliteStationnementError && (
                      <div className="mt-2 text-sm text-red-600">
                        Erreur : {disponibiliteStationnementError}
                      </div>
                    )}
                    {!disponibiliteStationnementLoading &&
                      !disponibiliteStationnementError &&
                      disponibiliteStationnementKpi?.message && (
                        <div className="mt-2 text-xs text-slate-500">
                          {disponibiliteStationnementKpi.message}
                        </div>
                      )}
                    {!disponibiliteStationnementLoading &&
                      !disponibiliteStationnementError &&
                      disponibiliteStationnementKpi?.disponibilite_stationnement_score_moyen !== undefined && (
                        <div className="mt-2 text-lg font-bold text-blue-900">
                          {disponibiliteStationnementKpi.disponibilite_stationnement_score_moyen}
                        </div>
                      )}
                  </div>
                )}

                {clickedPosition && (
                  <div className="mt-4 border-t border-blue-100 pt-3">
                    <div className="text-xs font-medium text-slate-600">Score activité quartier /100</div>
                    {activiteQuartierLoading && (
                      <div className="mt-2 text-sm text-slate-500">Chargement…</div>
                    )}
                    {!!activiteQuartierError && (
                      <div className="mt-2 text-sm text-red-600">
                        Erreur : {activiteQuartierError}
                      </div>
                    )}
                    {!activiteQuartierLoading &&
                      !activiteQuartierError &&
                      activiteQuartierKpi?.message && (
                        <div className="mt-2 text-xs text-slate-500">
                          {activiteQuartierKpi.message}
                        </div>
                      )}
                    {!activiteQuartierLoading &&
                      !activiteQuartierError &&
                      activiteQuartierKpi?.activite_quartier_score_moyen !== undefined && (
                        <div className="mt-2 text-lg font-bold text-blue-900">
                          {activiteQuartierKpi.activite_quartier_score_moyen}
                        </div>
                      )}
                  </div>
                )}

                {clickedPosition && (
                  <div className="mt-4 border-t border-blue-100 pt-3">
                    <div className="text-xs font-medium text-slate-600">Propreté générale /100</div>
                    {propreteGeneraleLoading && (
                      <div className="mt-2 text-sm text-slate-500">Chargement…</div>
                    )}
                    {!!propreteGeneraleError && (
                      <div className="mt-2 text-sm text-red-600">
                        Erreur : {propreteGeneraleError}
                      </div>
                    )}
                    {!propreteGeneraleLoading &&
                      !propreteGeneraleError &&
                      propreteGeneraleKpi?.message && (
                        <div className="mt-2 text-xs text-slate-500">
                          {propreteGeneraleKpi.message}
                        </div>
                      )}
                    {!propreteGeneraleLoading &&
                      !propreteGeneraleError &&
                      propreteGeneraleKpi?.proprete_score_moyen !== undefined && (
                        <div className="mt-2 text-lg font-bold text-blue-900">
                          {propreteGeneraleKpi.proprete_score_moyen}
                        </div>
                      )}
                  </div>
                )}
                
                {clickedPosition && (
                  <div className="mt-4 border-t border-blue-100 pt-3">
                    <div className="text-xs font-medium text-slate-600">Score de nuisance sonore /100</div>
                    {nuisanceSonoreLoading && (
                      <div className="mt-2 text-sm text-slate-500">Chargement…</div>
                    )}
                    {!!nuisanceSonoreError && (
                      <div className="mt-2 text-sm text-red-600">
                        Erreur : {nuisanceSonoreError}
                      </div>
                    )}
                    {!nuisanceSonoreLoading &&
                      !nuisanceSonoreError &&
                      nuisanceSonoreKpi?.message && (
                        <div className="mt-2 text-xs text-slate-500">
                          {nuisanceSonoreKpi.message}
                        </div>
                      )}
                    {!nuisanceSonoreLoading &&
                      !nuisanceSonoreError &&
                      nuisanceSonoreKpi?.avg_nuisance_sonore_score !== undefined && (
                        <div className="mt-2 text-lg font-bold text-blue-900">
                          {nuisanceSonoreKpi.avg_nuisance_sonore_score}
                        </div>
                      )}
                  </div>
                )}
              </div>
            </div>

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
