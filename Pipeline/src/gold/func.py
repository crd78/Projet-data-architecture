from shapely.geometry import Point, Polygon
import json
import pandas as pd

def point_dans_zone(x, y, df_path, arr=None, other_column=None):
    df = pd.read_parquet(df_path)

    if arr is not None:

        df = df[df['c_ar'] == arr].reset_index()


    is_in = False
    i = 0
    nom_quartier = ""
    num_quartier = 0


    point = Point(y, x)
    while not is_in and i < len(df):
        coordonnees_zone = json.loads(df["geometry"].iloc[i])
        polygone = Polygon(coordonnees_zone["coordinates"][0])

        if point.within(polygone):
            nom_quartier = df.iloc[i]["l_qu"]
            num_quartier = df.iloc[i]["c_quinsee"]

            if other_column is not None:
                other_values = df.iloc[i][other_column]
                return num_quartier, nom_quartier, other_values
            return num_quartier, nom_quartier
        i += 1
    if other_column is not None:
        return None, None, None
    return None, None


