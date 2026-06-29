import json
import re


def fix_coordinates(coords):
    """
    Corrige les coordonnées mal formatées (2,33 → 2.33)
    """
    fixed = []
    for lng, lat in coords:
        fixed.append(
            (float(str(lng).replace(",", ".")), float(str(lat).replace(",", ".")))
        )
    return fixed


def _coerce_ring(coords):
    fixed = []
    for coord in coords:
        if not isinstance(coord, (list, tuple)) or len(coord) < 2:
            continue
        lng = float(str(coord[0]).replace(",", "."))
        lat = float(str(coord[1]).replace(",", "."))
        fixed.append((lng, lat))
    return fixed


def extract_polygon(geometry_value):
    """
    Extrait un anneau de coordonnées à partir d'une géométrie GeoJSON,
    d'une string JSON, ou d'une string brute contenant des coordonnées.
    """
    if geometry_value is None:
        return None

    try:
        payload = geometry_value
        if isinstance(geometry_value, str):
            text = geometry_value.strip()
            if not text:
                return None
            if text.startswith("{") or text.startswith("["):
                payload = json.loads(text)
            else:
                payload = text

        if isinstance(payload, dict):
            geom_type = payload.get("type")
            coordinates = payload.get("coordinates")

            if geom_type == "Polygon" and coordinates:
                ring = _coerce_ring(coordinates[0])
                return ring if len(ring) >= 3 else None

            if geom_type == "MultiPolygon" and coordinates:
                ring = _coerce_ring(coordinates[0][0])
                return ring if len(ring) >= 3 else None

        if isinstance(payload, list):
            ring = _coerce_ring(payload[0] if payload and isinstance(payload[0], list) else payload)
            return ring if len(ring) >= 3 else None

        numbers = re.findall(r"[-+]?\d+,\d+|[-+]?\d+\.\d+|[-+]?\d+", str(payload))
        values = [float(n.replace(",", ".")) for n in numbers]
        coords = []
        for i in range(0, len(values), 2):
            if i + 1 < len(values):
                coords.append((values[i], values[i + 1]))
        return coords if len(coords) >= 3 else None

    except Exception:
        return None
