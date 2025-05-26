import geopandas as gpd  
import pandas as pd  
from pathlib import Path  

# Path to folder containing geojson files  
geojson_dir = Path("/path/to/geojson/folder")  

# Optional: list of columns to drop if present  
columns_to_drop = ["start_date", "end_date"]  

def load_and_clean(file):  
    gdf = gpd.read_file(file)  
    for col in columns_to_drop:  
        if col in gdf.columns:  
            gdf = gdf.drop(columns=col)  
    return gdf  

# Load and concatenate  
gdfs = [load_and_clean(f) for f in geojson_dir.glob("*.geojson")]  
combined = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True), crs="EPSG:4326")  

# Reproject to British National Grid for area calculation  
combined_proj = combined.to_crs(epsg=27700)  
combined_proj["area_m2"] = combined_proj.geometry.area  
combined_proj["area_ha"] = combined_proj["area_m2"] / 10000  

# Check result  
print(combined_proj[["area_m2", "area_ha"]].head())  

# Keep only key columns  
final = combined_proj[["id", "area_m2", "area_ha", "geometry"]]  

# Save both versions  
final.drop(columns="geometry").to_csv("geoJSONdata.csv", index=False)  
final.to_file("geoJSONdata-geom.geojson", driver="GeoJSON")  
