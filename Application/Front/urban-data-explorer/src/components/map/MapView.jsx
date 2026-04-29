import { useMemo, useState } from "react";
import DeckGL from "@deck.gl/react";
import "maplibre-gl/dist/maplibre-gl.css";
import useGeoJsonData from "../../hooks/useGeoJsonData";
import {
  createDistrictLabelLayer,
  createDistrictLayer,
  createRoadLayer,
} from "./GeoJsonLayer";

const INITIAL_VIEW_STATE = {
  longitude: 2.3522,
  latitude: 48.8566,
  zoom: 11,
  pitch: 0,
  bearing: 0,
};

function formatCoordinate(value) {
  return Number(value).toFixed(5);
}

function MapToolButton({ label, children, onClick }) {
  return (
    <button
      type="button"
      aria-label={label}
      title={label}
      onClick={onClick}
      className="grid h-11 w-11 place-items-center border-b border-[#e0e3e5] bg-white text-[#03071d] transition hover:bg-[#f2f4f6] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-[#3b82f6] last:border-b-0"
    >
      {children}
    </button>
  );
}

function MapView({ geoJsonUrl, selectedArrondissement = "all", onArrondissementSelect }) {
  const { data: arrondissementsData } = useGeoJsonData(geoJsonUrl);
  const { data: roadData } = useGeoJsonData("/data/voies.geojson");
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);
  const [lastCoordinate, setLastCoordinate] = useState(null);

  const showRoads = viewState.zoom >= 12.3;

  const layers = useMemo(() => {
    const output = [];

    if (arrondissementsData) {
      output.push(
        createDistrictLayer(arrondissementsData, "nom", true, selectedArrondissement),
        createDistrictLabelLayer(arrondissementsData, selectedArrondissement)
      );
    }

    if (roadData && showRoads) {
      output.push(createRoadLayer(roadData));
    }

    return output;
  }, [arrondissementsData, roadData, selectedArrondissement, showRoads]);

  const updateZoom = (delta) => {
    setViewState((current) => ({
      ...current,
      zoom: Math.max(10, Math.min(15.5, current.zoom + delta)),
    }));
  };

  const handleMapClick = (info) => {
    if (info?.coordinate) {
      const [longitude, latitude] = info.coordinate;
      setLastCoordinate({ longitude, latitude });
    }

    const code = info?.object?.properties?.code;
    if (code && info?.layer?.id === "district-layer") {
      onArrondissementSelect?.(code);
    }
  };

  return (
    <section className="map-canvas relative h-full w-full overflow-hidden">
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
          keyboard: false,
        }}
        layers={layers}
        style={{ position: "absolute", inset: 0, width: "100%", height: "100%" }}
        getTooltip={({ object, layer }) => {
          if (!object) return null;

          const p = object.properties || {};
          const isRoad = layer?.id === "road-layer";

          return {
            text: isRoad
              ? p.l_longmin || p.l_voie || p.l_courtmin || "Voie parisienne"
              : p.nom || p.name || "Arrondissement",
          };
        }}
      />

      <div className="pointer-events-none absolute bottom-4 right-4 z-20 flex flex-col items-end gap-3 sm:bottom-6 sm:right-6">
        <div className="pointer-events-auto overflow-hidden rounded-lg border border-[#c7c5ce] bg-white shadow-[0_10px_25px_-12px_rgba(26,31,54,0.28)]">
          <MapToolButton label="Zoom avant" onClick={() => updateZoom(0.6)}>
            <span className="text-2xl leading-none">+</span>
          </MapToolButton>
          <MapToolButton label="Zoom arrière" onClick={() => updateZoom(-0.6)}>
            <span className="text-2xl leading-none">-</span>
          </MapToolButton>
          <MapToolButton label="Recentrer Paris" onClick={() => setViewState(INITIAL_VIEW_STATE)}>
            <svg aria-hidden="true" className="h-5 w-5" viewBox="0 0 24 24" fill="none">
              <path
                d="M12 3v3M12 18v3M3 12h3M18 12h3M7.8 7.8l2.1 2.1M14.1 14.1l2.1 2.1M16.2 7.8l-2.1 2.1M9.9 14.1l-2.1 2.1"
                stroke="currentColor"
                strokeLinecap="round"
                strokeWidth="1.8"
              />
              <circle cx="12" cy="12" r="2.8" stroke="currentColor" strokeWidth="1.8" />
            </svg>
          </MapToolButton>
        </div>

        <div className="glass-panel pointer-events-auto rounded-lg px-3 py-2">
          <div className="inner-sheen" />
          <div className="flex items-center gap-2 text-xs font-semibold text-[#1a1f36]">
            <span className="h-2 w-2 rounded-full bg-[#3b82f6]" />
            {showRoads ? "Réseau viaire actif" : "Contours arrondissements"}
          </div>
          <div className="mt-1 font-['Space_Grotesk'] text-[11px] font-medium text-[#46464d]">
            Z {viewState.zoom.toFixed(1)}
            {lastCoordinate
              ? ` | ${formatCoordinate(lastCoordinate.latitude)}, ${formatCoordinate(
                  lastCoordinate.longitude
                )}`
              : " | Paris"}
          </div>
        </div>
      </div>
    </section>
  );
}

export default MapView;
