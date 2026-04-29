import { useState } from "react";
import KpiTemporalTab from "../kpi/tabs/KpiTemporalTab";
import KpiComparisonTab from "../kpi/tabs/KpiComparisonTab";

function FilterView(props) {
  const [activeTab, setActiveTab] = useState("temporal");

  const tabButtonBase = "rounded-xl px-5 py-2.5 text-base font-semibold transition-colors";
  const tabActive = "bg-blue-700 text-white";
  const tabInactive = "bg-blue-100 text-blue-900 hover:bg-blue-200";

  return (
    <aside className="h-full rounded-2xl border border-blue-100 bg-blue-50 shadow-sm flex flex-col">
      <div className="border-b border-blue-100 p-4">
        <div className="mt-1 flex gap-2">
          <button
            type="button"
            onClick={() => setActiveTab("temporal")}
            className={`${tabButtonBase} ${activeTab === "temporal" ? tabActive : tabInactive}`}
          >
            KPI temporels
          </button>
          <button
            type="button"
            onClick={() => setActiveTab("comparison")}
            className={`${tabButtonBase} ${activeTab === "comparison" ? tabActive : tabInactive}`}
          >
            Comparaison
          </button>
        </div>
      </div>

      <div className="p-4 space-y-4">
        {activeTab === "temporal" && <KpiTemporalTab {...props} />}
        {activeTab === "comparison" && <KpiComparisonTab {...props} />}
      </div>
    </aside>
  );
}

export default FilterView;