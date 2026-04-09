import { GeoJsonLayer as DeckGeoJsonLayer } from "@deck.gl/layers";

function colorFromString(value) {
    const str = String(value ?? "default");
    let hash = 0;

    for (let i = 0; i < str.length; i += 1) {
        hash = str.charCodeAt(i) + ((hash << 5) - hash);
    }

    const hue = Math.abs(hash) % 360;
    return [hue, 70, 48];
}

function hslToRgba(h, s, l, a) {
    const sat = s / 100;
    const lig = l / 100;
    const c = (1 - Math.abs(2 * lig - 1)) * sat;
    const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
    const m = lig - c / 2;

    let r = 0;
    let g = 0;
    let b = 0;

    if (h < 60) [r, g, b] = [c, x, 0];
    else if (h < 120) [r, g, b] = [x, c, 0];
    else if (h < 180) [r, g, b] = [0, c, x];
    else if (h < 240) [r, g, b] = [0, x, c];
    else if (h < 300) [r, g, b] = [x, 0, c];
    else [r, g, b] = [c, 0, x];

    return [
        Math.round((r + m) * 255),
        Math.round((g + m) * 255),
        Math.round((b + m) * 255),
        a
    ];
}

export function createGeoJsonLayer(data, colorProperty = "nom") {
    return new DeckGeoJsonLayer({
    id: "geojson-layer",
    data,
    pickable: true,
    stroked: true,
    filled: true,
    autoHighlight: true,
    lineWidthMinPixels: 1.2,
    highlightColor: [255, 140, 0, 160],
    getLineColor: [30, 64, 175, 220],
    getFillColor: (feature) => {
    const [h, s, l] = colorFromString(feature?.properties?.[colorProperty]);
    return hslToRgba(h, s, l, 90);
    },
    getPointRadius: 80
    });
}