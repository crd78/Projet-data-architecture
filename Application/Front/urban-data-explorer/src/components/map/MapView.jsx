import { useMemo, useState } from "react";
import DeckGL from "@deck.gl/react";
import { Map } from "react-map-gl/maplibre";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";
import useGeoJsonData from "../../hooks/useGeoJsonData";
import { createGeoJsonLayer } from "./GeoJsonLayer";
import MapLegend from "./MapLegend";
import MapControls from "./MapControls";

const INITIAL_VIEW_STATE = {
    longitude: 2.3522,
    latitude: 48.8566,
    zoom: 10,
    pitch: 0,
    bearing: 0
};

const MAP_STYLE = "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json";

function MapView({ geoJsonUrl }) {
    const { data, loading, error } = useGeoJsonData(geoJsonUrl);
    const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);

    const layers = useMemo(() => {
    if (!data) return [];
    return [createGeoJsonLayer(data, "nom")];
    }, [data]);

    const featureCount = data?.features?.length ?? 0;
    return (
        <section className="relative h-[75vh] w-full overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm">
            <DeckGL
                viewState={viewState}
                onViewStateChange={({ viewState: next }) => setViewState(next)}
                controller
                layers={layers}
                getTooltip={({ object }) => {
                if (!object) return null;
                const props = object.properties || {};
                return { text: props.nom || props.name || "Feature" };
                }}
            ></DeckGL>
            <MapControls onReset={() => setViewState(INITIAL_VIEW_STATE)} />
            <MapLegend loading={loading} error={error} featureCount={featureCount} />
        </section>
    );
}

export default MapView;
