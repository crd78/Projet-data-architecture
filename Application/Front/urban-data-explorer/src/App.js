import {useEffect, useMemo, useState} from "react";
import DeckGL from "@deck.gl/react";
import {GeoJsonLayer} from "@deck.gl/layers";
import {Map} from "react-map-gl/maplibre";
import "maplibre-gl/dist/maplibre-gl.css";

const INITIAL_VIEW_STATE = {
  longitude: 2.3522,
  latitude: 48.8566,
  zoom: 10,
  pitch: 0,
  bearing: 0
};

const MAP_STYLE = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json";

function App() {
  const [data, setData] = useState(null);

  useEffect(() => {
    fetch("/data/communes.geojson")
      .then((res) => {
        if (!res.ok) throw new Error("Impossible de charger le GeoJSON");
        return res.json();
      })
      .then(setData)
      .catch((err) => console.error(err));
  }, []);

  const layers = useMemo(() => {
    if (!data) return [];

    return [
      new GeoJsonLayer({
        id: "geojson-layer",
        data,
        stroked: true,
        filled: true,
        pickable: true,
        lineWidthMinPixels: 1,
        getLineColor: [30, 64, 175, 220],
        getFillColor: [59, 130, 246, 80],
        getPointRadius: 100,
        autoHighlight: true
      })
    ];
  }, [data]);

  return (
    <main className="h-screen w-screen">
      <DeckGL
        initialViewState={INITIAL_VIEW_STATE}
        controller={true}
        layers={layers}
      >
        <Map mapStyle={MAP_STYLE} />
      </DeckGL>
    </main>
  );
}

export default App;