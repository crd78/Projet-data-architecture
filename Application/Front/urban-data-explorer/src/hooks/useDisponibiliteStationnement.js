import { useEffect, useState } from "react";
import { fetchDisponibiliteStationnement } from "../services/kpiService";

function useDisponibiliteStationnement(clickedPosition) {
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

      const payload = await fetchDisponibiliteStationnement(
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

export default useDisponibiliteStationnement;