import json
from functools import lru_cache
from pathlib import Path

import pandas as pd
from shapely import wkt
from shapely.geometry import Point, shape
from shapely.prepared import prep


def _parse_geometry(value):
    if value is None or pd.isna(value):
        return None

    if hasattr(value, "__geo_interface__"):
        return value

    text = str(value).strip()
    if not text:
        return None

    if text.startswith("{") or text.startswith("["):
        payload = json.loads(text)
        if isinstance(payload, dict):
            return shape(payload)

    return wkt.loads(text)


@lru_cache(maxsize=8)
def _load_zones(df_path: str):
    df = pd.read_parquet(Path(df_path))
    zones = []

    for _, row in df.iterrows():
        geometry_value = row.get("geometry") if "geometry" in df.columns else row.get("geometry_quartier")
        geom = _parse_geometry(geometry_value)
        if geom is None or geom.is_empty:
            continue

        zones.append(
            {
                "arrondissement": row.get("c_ar", row.get("arrondissement_quartier")),
                "nom_quartier": row.get("l_qu", row.get("nom_quartier")),
                "num_quartier": row.get("c_qu", row.get("num_quartier")),
                "surface": row.get("surface", row.get("surface_quartier")),
                "geometry": str(geometry_value),
                "bounds": geom.bounds,
                "prepared": prep(geom),
            }
        )

    return tuple(zones)


def point_dans_zone(x, y, df_path, arr=None):
    if pd.isna(x) or pd.isna(y):
        return None, None, None, None

    point = Point(float(y), float(x))
    zones = _load_zones(str(df_path))

    for zone in zones:
        if arr is not None and zone["arrondissement"] != arr:
            continue

        minx, miny, maxx, maxy = zone["bounds"]
        if not (minx <= point.x <= maxx and miny <= point.y <= maxy):
            continue

        if zone["prepared"].contains(point):
            return zone["num_quartier"], zone["nom_quartier"], zone["surface"], zone["geometry"]

    return None, None, None, None

