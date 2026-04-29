import { useMemo, useState } from "react";

const tabs = [
  { id: "temporal", label: "Temporel" },
  { id: "territory", label: "Territoire" },
  { id: "operations", label: "Opérations" },
];

function formatRentValue(value) {
  const numericValue = Number(value);
  if (!Number.isFinite(numericValue)) return null;

  return new Intl.NumberFormat("fr-FR", {
    maximumFractionDigits: 0,
  }).format(numericValue);
}

function Sparkline({ tone = "emerald" }) {
  const heights = [42, 58, 52, 76, 64, 86, 72];
  const color = tone === "blue" ? "bg-[#3b82f6]" : "bg-[#10b981]";

  return (
    <div className="mt-4 flex h-12 items-end gap-1">
      {heights.map((height, index) => (
        <span
          key={`${height}-${index}`}
          className={`w-full rounded-sm ${color} ${index === heights.length - 1 ? "opacity-100" : "opacity-25"}`}
          style={{ height: `${height}%` }}
        />
      ))}
    </div>
  );
}

function KpiCard({ label, value, suffix, caption, status, tone = "emerald", loading, error }) {
  const toneClasses =
    tone === "blue"
      ? "bg-[#d8e2ff] text-[#004395]"
      : "bg-[#6cf8bb] text-[#005236]";

  return (
    <article className="rounded-lg border border-[#e0e3e5] bg-white p-4 shadow-[0_10px_25px_-18px_rgba(26,31,54,0.22)]">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="text-[11px] font-bold uppercase tracking-[0.14em] text-[#77767e]">
            {label}
          </p>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-[30px] font-semibold leading-none tracking-normal text-[#03071d]">
              {loading ? "..." : value}
            </span>
            {suffix && !loading && (
              <span className="text-sm font-semibold text-[#8286a2]">{suffix}</span>
            )}
          </div>
        </div>

        <span className={`shrink-0 rounded-full px-2.5 py-1 text-[10px] font-bold uppercase ${toneClasses}`}>
          {status}
        </span>
      </div>

      {error ? (
        <p className="mt-3 rounded-lg bg-[#ffdad6] px-3 py-2 text-xs font-semibold text-[#93000a]">
          {error}
        </p>
      ) : (
        <p className="mt-3 text-sm leading-5 text-[#46464d]">{caption}</p>
      )}
      <Sparkline tone={tone} />
    </article>
  );
}

function SignalRow({ label, detail, value, tone = "blue" }) {
  const toneClasses =
    tone === "emerald"
      ? "bg-[#6cf8bb] text-[#005236]"
      : tone === "dark"
        ? "bg-[#dde1ff] text-[#151a31]"
        : "bg-[#d8e2ff] text-[#004395]";

  return (
    <div className="flex items-center justify-between gap-4 rounded-lg border border-[#e0e3e5] bg-white px-3 py-3 odd:bg-[#f7f9fb]">
      <div className="min-w-0">
        <p className="truncate text-sm font-semibold text-[#1a1f36]">{label}</p>
        <p className="mt-1 truncate text-xs text-[#77767e]">{detail}</p>
      </div>
      <span className={`shrink-0 rounded-full px-2.5 py-1 font-['Space_Grotesk'] text-xs font-medium ${toneClasses}`}>
        {value}
      </span>
    </div>
  );
}

function FilterView({
  selectedYear,
  selectedArrondissement,
  arrondissementNumber,
  districtLabel,
  medianKpi,
  medianKpiLoading,
  medianKpiError,
}) {
  const [activeTab, setActiveTab] = useState("temporal");

  const formattedRent = formatRentValue(medianKpi?.median_price_loyer);
  const rentValue = useMemo(() => {
    if (selectedArrondissement === "all") return "--";
    if (formattedRent) return formattedRent;
    return "ND";
  }, [formattedRent, selectedArrondissement]);

  const contextRows = [
    {
      label: "Périmètre d'analyse",
      detail: districtLabel,
      value: selectedArrondissement === "all" ? "Global" : `A${arrondissementNumber}`,
      tone: "dark",
    },
    {
      label: "Millésime",
      detail: "Fenetre temporelle du datamart",
      value: selectedYear,
      tone: "blue",
    },
    {
      label: "Granularité",
      detail: "Contours administratifs de Paris",
      value: "IRIS",
      tone: "emerald",
    },
  ];

  const backlogRows = [
    {
      label: "Parc immobilier",
      detail: "Répartition typologique à connecter",
      value: "Prêt",
      tone: "dark",
    },
    {
      label: "Logements sociaux",
      detail: "Signal métier réservé au prochain flux",
      value: "Source",
      tone: "blue",
    },
    {
      label: "Nuisance sonore",
      detail: "Indice de confort urbain en attente",
      value: "Queue",
      tone: "emerald",
    },
    {
      label: "Accessibilité",
      detail: "Stations et voirie détaillées au zoom",
      value: "Zoom",
      tone: "blue",
    },
  ];

  return (
    <section className="space-y-5">
      <div className="grid grid-cols-3 gap-1 rounded-lg bg-[#f2f4f6] p-1">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`rounded-md px-2 py-2 text-xs font-bold transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#3b82f6] ${
              activeTab === tab.id
                ? "bg-[#1a1f36] text-white shadow-sm"
                : "text-[#46464d] hover:bg-white"
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {activeTab === "temporal" && (
        <div className="space-y-4">
          <KpiCard
            label="Loyer médian"
            value={rentValue}
            suffix={formattedRent ? "€/m²" : ""}
            status={selectedArrondissement === "all" ? "Choix requis" : "API"}
            caption={
              selectedArrondissement === "all"
                ? "Sélectionnez un arrondissement pour interroger le KPI médian."
                : `Lecture du datamart pour ${districtLabel}, année ${selectedYear}.`
            }
            loading={medianKpiLoading}
            error={medianKpiError}
          />

          <KpiCard
            label="Couverture temporelle"
            value="5"
            suffix="ans"
            status="Stable"
            tone="blue"
            caption="Le front expose une fenêtre 2019-2023 pour comparer les millésimes disponibles."
          />
        </div>
      )}

      {activeTab === "territory" && (
        <div className="space-y-3">
          {contextRows.map((row) => (
            <SignalRow key={row.label} {...row} />
          ))}
        </div>
      )}

      {activeTab === "operations" && (
        <div className="space-y-3">
          {backlogRows.map((row) => (
            <SignalRow key={row.label} {...row} />
          ))}
        </div>
      )}
    </section>
  );
}

export default FilterView;
