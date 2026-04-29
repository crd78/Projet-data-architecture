import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


def point_dans_zone(latitude, longitude, quartiers_path, arrondissement=None, other_column=None):
    """
    Détermine le quartier pour un point donné.
    
    Args:
        latitude: Latitude du point
        longitude: Longitude du point
        quartiers_path: Chemin vers le fichier parquet des quartiers
        arrondissement: Arrondissement optionnel pour filtrage
        other_column: Colonne supplémentaire à retourner (ex: 'surface')
    
    Returns:
        pd.Series avec [num_quartier, nom_quartier] ou [num_quartier, nom_quartier, other_column]
    """
    try:
        if pd.isna(latitude) or pd.isna(longitude):
            result = [None, None]
            if other_column:
                result.append(None)
            return pd.Series(result)
        
        # Lire le parquet
        gdf = gpd.read_parquet(quartiers_pat)
        
        # Filtrer par arrondissement si fourni
        if arrondissement is not None:
            gdf = gdf[gdf['c_ar'] == arrondissement]
        
        # Créer le point
        point = Point(float(longitude), float(latitude))
        
        # Chercher le quartier contenant le point
        mask = gdf.geometry.contains(point)
        
        if mask.any():
            row = gdf[mask].iloc[0]
            result = [row['c_qu'], row['l_qu']]
            if other_column and other_column in row:
                result.append(row[other_column])
            return pd.Series(result)
    except Exception:
        pass
    
    # Aucun résultat trouvé
    result = [None, None]
    if other_column:
        result.append(None)
    return pd.Series(result)
