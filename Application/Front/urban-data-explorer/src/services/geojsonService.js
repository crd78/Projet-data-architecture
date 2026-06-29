export async function fetchGeoJson(url) {
const response = await fetch(url);

if (!response.ok) {
throw new Error(`Erreur HTTP ${response.status} pendant le chargement de ${url}`);
}

const data = await response.json();

if (!data || data.type !== "FeatureCollection") {
throw new Error("Le fichier charge n'est pas un GeoJSON FeatureCollection valide.");
}

return data;
}