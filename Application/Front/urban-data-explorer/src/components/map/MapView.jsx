import { useMemo, useState } from "react";
import DeckGL from "@deck.gl/react";
import "maplibre-gl/dist/maplibre-gl.css";
import useGeoJsonData from "../../hooks/useGeoJsonData";
import { createGeoJsonLayer } from "./GeoJsonLayer";

const INITIAL_VIEW_STATE = {
    longitude: 2.3522,
    latitude: 48.8566,
    zoom: 11,
};


function MapView({ geoJsonUrl }) {
    const { data } = useGeoJsonData(geoJsonUrl);
    const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);

    const layers = useMemo(() => {
    if (!data) return [];
    return [createGeoJsonLayer(data, "nom")];
    }, [data]);

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
                const props = object.properties || {};
                return { text: props.nom || props.name || "Feature" };
            }}
            />
        </section>
    );
}

export default MapView;
