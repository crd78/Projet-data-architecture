import { useEffect, useState } from "react";
import { fetchMedianPricePerArrondissement } from "../services/kpiService";

function useMedianKpi(selectedYear, arrondissementNumber, mode = "location") {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!arrondissementNumber) {
      setData(null);
      setError("");
      setLoading(false);
      return;
    }

    const controller = new AbortController();

    async function load() {
      setLoading(true);
      setError("");

      const payload = await fetchMedianPricePerArrondissement(
        selectedYear,
        arrondissementNumber,
        mode,
        controller.signal
      );

      setData(payload);
    }

    load()
      .catch((err) => {
        if (err.name === "AbortError") return;
        setError(err.message || "Erreur inconnue");
        setData(null);
      })
      .finally(() => setLoading(false));

    return () => controller.abort();
  }, [selectedYear, arrondissementNumber, mode]);

  return { data, loading, error };
}

export default useMedianKpi;