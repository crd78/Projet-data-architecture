import { useEffect, useState } from "react";
import { fetchAccessibiliteLoyerRevenu } from "../services/kpiService";

function useAccessibiliteKpi(selectedYear, arrondissementNumber, revenuProportion) {
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

      const payload = await fetchAccessibiliteLoyerRevenu(
        selectedYear,
        arrondissementNumber,
        revenuProportion,
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
  }, [selectedYear, arrondissementNumber, revenuProportion]);

  return { data, loading, error };
}

export default useAccessibiliteKpi;