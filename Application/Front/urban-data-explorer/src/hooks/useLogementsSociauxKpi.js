import { useEffect, useState } from "react";
import { fetchLogementsSociauxTotal } from "../services/kpiService";

function useLogementsSociauxKpi(selectedYear, arrondissementNumber) {
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

      const payload = await fetchLogementsSociauxTotal(
        selectedYear,
        arrondissementNumber,
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
  }, [selectedYear, arrondissementNumber]);

  return { data, loading, error };
}

export default useLogementsSociauxKpi;