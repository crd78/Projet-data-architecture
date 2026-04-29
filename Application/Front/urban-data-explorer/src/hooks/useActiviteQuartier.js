import { useEffect, useState } from "react";
import { fetchActiviteQuartier } from "../services/kpiService";

function useActiviteQuartier(clickedPosition) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!clickedPosition?.longitude || !clickedPosition?.latitude) {
      setData(null);
      setError("");
      setLoading(false);
      return;
    }

    const controller = new AbortController();

    async function load() {
      setLoading(true);
      setError("");

      const payload = await fetchActiviteQuartier(
        clickedPosition.longitude,
        clickedPosition.latitude,
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
  }, [clickedPosition?.longitude, clickedPosition?.latitude]);

  return { data, loading, error };
}

export default useActiviteQuartier;