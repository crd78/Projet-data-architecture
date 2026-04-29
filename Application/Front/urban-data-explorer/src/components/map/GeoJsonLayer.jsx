import { GeoJsonLayer as DeckGeoJsonLayer, TextLayer } from "@deck.gl/layers";

const DISTRICT_PALETTE = [
  [59, 130, 246],
  [16, 185, 129],
  [14, 165, 233],
  [0, 108, 73],
  [88, 93, 119],
  [0, 67, 149],
];

function getArrondissementNumber(code) {
  const match = String(code ?? "").match(/(\d{2})$/);
  return match ? Number(match[1]) : 0;
}

function getDistrictColor(feature) {
  const index = getArrondissementNumber(feature?.properties?.code) % DISTRICT_PALETTE.length;
  return DISTRICT_PALETTE[index];
}

function collectPositions(coords, output = []) {
  if (!Array.isArray(coords)) return output;

  if (typeof coords[0] === "number" && typeof coords[1] === "number") {
    output.push(coords);
    return output;
  }

  coords.forEach((child) => collectPositions(child, output));
  return output;
}

function getFeatureCenter(feature) {
  const positions = collectPositions(feature?.geometry?.coordinates);
  if (!positions.length) return [2.3522, 48.8566];

  const sum = positions.reduce(
    (acc, position) => [acc[0] + position[0], acc[1] + position[1]],
    [0, 0]
  );

  return [sum[0] / positions.length, sum[1] / positions.length];
}

function formatDistrictShortName(code) {
  const number = getArrondissementNumber(code);
  if (!number) return "";
  return number === 1 ? "1er" : `${number}e`;
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
    highlightColor: [16, 185, 129, 95],

    lineWidthUnits: "pixels",
    lineWidthScale: 1,
    lineWidthMinPixels: 1.2,

    getLineColor: (feature) => {
      const isSelected = hasSelection && feature?.properties?.code === selectedCode;
      return isSelected ? [255, 255, 255, 245] : [26, 31, 54, 175];
    },

    getLineWidth: (feature) => {
      const isSelected = hasSelection && feature?.properties?.code === selectedCode;
      return isSelected ? 4 : 1.4;
    },

    getFillColor: (feature) => {
      const color = getDistrictColor(feature?.properties?.[colorProperty] ? feature : null);
      const isSelected = hasSelection && feature?.properties?.code === selectedCode;

      if (!hasSelection) return [...color, 105];
      return isSelected ? [16, 185, 129, 190] : [...color, 62];
    },

    updateTriggers: {
      getLineColor: selectedCode,
      getLineWidth: selectedCode,
      getFillColor: selectedCode,
    },
  });
}

export function createDistrictLabelLayer(data, selectedCode = "all") {
  const labels = (data?.features || []).map((feature) => ({
    code: feature?.properties?.code,
    label: formatDistrictShortName(feature?.properties?.code),
    position: getFeatureCenter(feature),
  }));
  const hasSelection = selectedCode && selectedCode !== "all";

  return new TextLayer({
    id: "district-label-layer",
    data: labels,
    pickable: false,
    getPosition: (d) => d.position,
    getText: (d) => d.label,
    getSize: (d) => (hasSelection && d.code === selectedCode ? 18 : 13),
    getColor: (d) =>
      hasSelection && d.code === selectedCode ? [3, 7, 29, 245] : [3, 7, 29, 170],
    getAngle: 0,
    getTextAnchor: "middle",
    getAlignmentBaseline: "center",
    fontFamily: "Inter, Arial, sans-serif",
    fontWeight: 700,
    outlineColor: [255, 255, 255, 210],
    outlineWidth: 3,
    sizeUnits: "pixels",
    updateTriggers: {
      getSize: selectedCode,
      getColor: selectedCode,
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
    highlightColor: [16, 185, 129, 180],
    lineWidthScale: 1,
    lineWidthMinPixels: 1,
    getLineWidth: 1,
    getLineColor: [59, 130, 246, 185],
  });
}
