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
        geom = _parse_geometry(row.get("geometry"))
        if geom is None or geom.is_empty:
            continue

        zones.append(
            {
                "arrondissement": row.get("c_ar"),
                "nom_quartier": row.get("l_qu"),
                "num_quartier": row.get("c_quinsee"),
                "surface": row.get("surface"),
                "bounds": geom.bounds,
                "prepared": prep(geom),
            }
        )

    return tuple(zones)


def point_dans_zone(x, y, df_path, arr=None, other_column=None):
    if pd.isna(x) or pd.isna(y):
        if other_column is not None:
            return None, None, None
        return None, None

    point = Point(float(y), float(x))
    zones = _load_zones(str(df_path))

    for zone in zones:
        if arr is not None and zone["arrondissement"] != arr:
            continue

        minx, miny, maxx, maxy = zone["bounds"]
        if not (minx <= point.x <= maxx and miny <= point.y <= maxy):
            continue

        if zone["prepared"].contains(point):
            if other_column is not None:
                return zone["num_quartier"], zone["nom_quartier"], zone.get(other_column)
            return zone["num_quartier"], zone["nom_quartier"]

    if other_column is not None:
        return None, None, None
    return None, None
