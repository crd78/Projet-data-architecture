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
    a,
  ];
}

export function createDistrictLayer(
  data,
  colorProperty = "nom",
  pickable = true,
  selectedCode = "all"
) {
  const hasSelection = selectedCode && selectedCode !== "all";

  return new DeckGeoJsonLayer({
    id: "district-layer",
    data,
    pickable,
    stroked: true,
    filled: true,
    autoHighlight: true,

    highlightColor: [255, 140, 0, 160],

    lineWidthUnits: "pixels",
    lineWidthScale: 1,
    lineWidthMinPixels: 1.2,

    getLineColor: (feature) => {
      const isSelected = hasSelection && feature?.properties?.code === selectedCode;
      return isSelected ? [255, 140, 0, 255] : [30, 64, 175, 200];
    },

    getLineWidth: (feature) => {
      const isSelected = hasSelection && feature?.properties?.code === selectedCode;
      return isSelected ? 4 : 1.5;
    },

    getFillColor: (feature) => {
      const [h, s, l] = colorFromString(feature?.properties?.[colorProperty]);
      const isSelected = hasSelection && feature?.properties?.code === selectedCode;

      // Tous restent visibles ; le sélectionné ressort surtout par le contour
      const alpha = !hasSelection ? 90 : isSelected ? 140 : 90;
      return hslToRgba(h, s, l, alpha);
    },

    updateTriggers: {
    getLineColor: selectedCode,
    getLineWidth: selectedCode,
    getFillColor: selectedCode,
  },
  
  });
}

export function createRoadLayer(data) {
  return new DeckGeoJsonLayer({
    id: "road-layer",
    data,
    pickable: true,
    stroked: true,
    filled: false,
    autoHighlight: true,
    highlightColor: [15, 23, 42, 180],
    lineWidthScale: 1,
    lineWidthMinPixels: 1,
    getLineWidth: 1,
    getLineColor: [37, 99, 235, 190],
  });
}