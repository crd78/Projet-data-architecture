import { useMemo, useState } from "react";
import DeckGL from "@deck.gl/react";
import "maplibre-gl/dist/maplibre-gl.css";
import useGeoJsonData from "../../hooks/useGeoJsonData";
import { createDistrictLayer, createRoadLayer } from "./GeoJsonLayer";
import { IconLayer } from "@deck.gl/layers";

const INITIAL_VIEW_STATE = {
  longitude: 2.3522,
  latitude: 48.8566,
  zoom: 11
};

function MapView({ geoJsonUrl, selectedArrondissement = "all", onMapClick}) {
  const { data: arrondissementsData } = useGeoJsonData(geoJsonUrl);
  const { data: roadData } = useGeoJsonData("/data/voies.geojson");
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);
  const [clickedPosition, setClickedPosition] = useState(null);

  const layers = useMemo(() => {
    const output = [];
    const showRoads = viewState.zoom >= 12.3;

    if (arrondissementsData) {
      output.push(
        createDistrictLayer(
          arrondissementsData,
          "nom",
          !showRoads,
          selectedArrondissement
        )
      );
    }

    if (roadData && showRoads) {
      output.push(createRoadLayer(roadData));
    }

    if (clickedPosition) {
      output.push(
        new IconLayer({
          id: "click-marker",
          data: [clickedPosition],
          getPosition: (d) => [d.longitude, d.latitude],
          getIcon: () => ({
            url: "/marker.png",
            width: 64,
            height: 64,
            anchorY: 64
          }),
          sizeScale: 1,
          getSize: 30,
          pickable: false
        })
      );
    }

    return output;
  }, [arrondissementsData, roadData, viewState.zoom, selectedArrondissement, clickedPosition]);

  const handleMapClick = (info) => {
    if (!info?.coordinate) return;

    const [longitude, latitude] = info.coordinate;
    const nextPosition = { longitude, latitude };

    setClickedPosition(nextPosition);
    onMapClick?.(nextPosition);

    console.log("Coordonnees :", nextPosition);
  };

  return (
    <section className="relative isolate h-[85vh] w-full overflow-hidden rounded-2xl border border-slate-200 bg-slate-200 shadow-sm">
      <DeckGL
        viewState={viewState}
        onViewStateChange={({ viewState: next }) => setViewState(next)}
        onClick={handleMapClick}
        controller={{
          dragPan: true,
          dragRotate: false,
          touchRotate: false,
          scrollZoom: true,
          doubleClickZoom: false,
          touchZoom: true,
          keyboard: false
        }}
        layers={layers}
        style={{ position: "absolute", top: 0, left: 0, width: "100%", height: "100%" }}
        getTooltip={({ object, layer }) => {
          if (!object) return null;

          const p = object.properties || {};
          const isRoad = layer?.id === "road-layer";

          if (isRoad) {
            return {
              text: p.l_longmin || p.l_voie || p.l_courtmin || "Voie"
            };
          }

          return {
            text: p.nom || p.name || "Arrondissement"
          };
        }}
      />
    </section>
  );
}

export default MapView;