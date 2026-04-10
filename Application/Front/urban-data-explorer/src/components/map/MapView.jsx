import { useMemo, useState } from "react";
import DeckGL from "@deck.gl/react";
import "maplibre-gl/dist/maplibre-gl.css";
import useGeoJsonData from "../../hooks/useGeoJsonData";
import { createDistrictLayer, createRoadLayer } from "./GeoJsonLayer";

const INITIAL_VIEW_STATE = {
  longitude: 2.3522,
  latitude: 48.8566,
  zoom: 11
};

function MapView({ geoJsonUrl }) {
  const { data: districtData } = useGeoJsonData(geoJsonUrl);
  const { data: roadData } = useGeoJsonData("/data/voies.geojson");
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);

  const layers = useMemo(() => {
    const output = [];

    if (districtData) {
      output.push(createDistrictLayer(districtData, "nom"));
    }

    const showRoads = viewState.zoom >= 11;
    if (roadData && showRoads) {
      output.push(createRoadLayer(roadData));
    }

    return output;
  }, [districtData, roadData, viewState.zoom]);

  return (
    <section className="relative isolate h-[85vh] w-full overflow-hidden rounded-2xl border border-slate-200 bg-slate-200 shadow-sm">
      <DeckGL
        viewState={viewState}
        onViewStateChange={({ viewState: next }) => setViewState(next)}
        controller={{
          dragPan: false,
          dragRotate: false,
          touchRotate: false,
          scrollZoom: false,
          doubleClickZoom: false,
          touchZoom: false,
          keyboard: false
        }}
        layers={layers}
        style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%" }}
        getTooltip={({ object }) => {
          if (!object) return null;
          const p = object.properties || {};
          return { text: p.nom || p.l_longmin || p.l_voie || "Feature" };
        }}
      />
    </section>
  );
}

export default MapView;