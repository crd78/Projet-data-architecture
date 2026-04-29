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


def extract_polygon(geo_shape_str):
    """
    Extrait les coordonnées depuis une string dégueu type:
    [[[2,3312, 48,8771], [...]]]
    """
    try:
        # récupère tous les nombres (y compris avec virgule)
        numbers = re.findall(r"[-+]?\d+,\d+|[-+]?\d+\.\d+|[-+]?\d+", geo_shape_str)

        # convertir en float propre
        values = [float(n.replace(",", ".")) for n in numbers]

        # grouper par 2 → (lng, lat)
        coords = []
        for i in range(0, len(values), 2):
            if i + 1 < len(values):
                lng = values[i]
                lat = values[i + 1]
                coords.append((lng, lat))
        return coords

    except Exception:
        return None
