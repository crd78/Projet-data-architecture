import { useMemo, useState } from "react";
import DeckGL from "@deck.gl/react";
import "maplibre-gl/dist/maplibre-gl.css";
import useGeoJsonData from "../../hooks/useGeoJsonData";
import { createGeoJsonLayer } from "./GeoJsonLayer";

const INITIAL_VIEW_STATE = {
    longitude: 2.3522,
    latitude: 48.8566,
    zoom: 10,
    pitch: 0,
    bearing: 0
};


function MapView({ geoJsonUrl }) {
    const { data } = useGeoJsonData(geoJsonUrl);
    const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);

    const layers = useMemo(() => {
    if (!data) return [];
    return [createGeoJsonLayer(data, "nom")];
    }, [data]);

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
        </section>
    );
}

export default MapView;
