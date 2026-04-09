import { useEffect, useState } from "react";
import { fetchGeoJson } from "../services/geojsonService";

function useGeoJsonData(url) {
const [data, setData] = useState(null);
const [loading, setLoading] = useState(true);
const [error, setError] = useState("");

useEffect(() => {
let isMounted = true;

async function load() {
    try {
        setLoading(true);
        setError("");
        const geojson = await fetchGeoJson(url);
        if (isMounted) setData(geojson);
    } catch (err) {
        if (isMounted) setError(err.message || "Erreur inconnue");
    } finally {
        if (isMounted) setLoading(false);
    }
}

load();

return () => {
isMounted = false;
};
}, [url]);

return { data, loading, error };
}

export default useGeoJsonData;