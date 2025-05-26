# 🏭 OpenStreetMap Industrial Estates Mapping Project

## 🏗️ Project Overview

This project was developed for a client in the green technology sector who wanted to identify and explore industrial estates in a specific region (East Midlands, UK) as potential sites for deploying their solution. The goal was to create a repeatable, low-cost method for extracting real-world property data from OpenStreetMap, cleaning it, and visualising it interactively in Tableau.

Key output: an **interactive visualisation** that enabled the client to quickly identify potential locations on a map, and then explore these further with built in functions that: 
- display the property outline on OMS
- search Google by property name
- search Google by GPS co-ordinates

<img width="700" alt="image" src="https://github.com/user-attachments/assets/a811f4b4-d0a9-49e7-991d-ca452707fd90" />
<br></br>
<img width="700" alt="image" src="https://github.com/user-attachments/assets/1a60aaba-4615-43c0-966d-1209b6247297" />
<br></br>


Beyond this specific use case, the workflow has broader applications for:

- Urban planning and land use analysis  
- Commercial site prospecting  
- Logistics and infrastructure mapping  
- Environmental impact studies  
- Academic or civic research using open geodata  

It demonstrates a flexible pipeline using freely available tools and data, and can be adapted for different property types, industries, or regions.

---

## 🔄 Workflow

The end-to-end workflow consists of the following steps:

### 1. Extract Location Data via Overpass Turbo

Use [https://overpass-turbo.eu/](https://overpass-turbo.eu/) to query OpenStreetMap for all relevant locations in the chosen region. For example, industrial estates in the East Midlands can be extracted using a custom Overpass query like:

```  
[out:json][timeout:60];  
area["name"="East Midlands"]->.searchArea;  
(  
  node["landuse"="industrial"](area.searchArea);  
  way["landuse"="industrial"](area.searchArea);  
  relation["landuse"="industrial"](area.searchArea);  
);  
out body;  
>;  
out skel qt;  
``` 

### 2. Export as GeoJSON

Once the query returns results, use Overpass Turbo’s **Export → GeoJSON** function to save the dataset.

### 3. Convert GeoJSON to CSV

Go to [https://geojson.io](https://geojson.io/) and drag in the GeoJSON file. Use the **Save As → CSV** option to convert and download the data in tabular format.

### 4. Clean the CSV in Excel

- Remove any entries without a `name` (since this is used for searching later)
- Optionally rename fields or remove nulls/duplicates as needed

### 5. Generate ID Strings for Boundary Queries

Create a new calculated column in Excel to convert the `@id` field from this format:

``` 
way/1234567  
```  

…to this format (suitable for use in Overpass to retrieve boundaries):

``` 
way(1234567);  
```  

Here’s the Excel formula you can use:

```  
="way("&MID([@id],FIND("/",[@id])+1,LEN([@id]))&");"  
```  

### 6. Retrieve Boundary Data in Batches

Paste these `way(...)` statements into Overpass Turbo in batches of around 200. Use a query like:

```  
[out:json][timeout:60];  
(  
  way(1234567);  
  way(1234568);  
  way(1234569);  
  ...  
);  
(._;>;);  
out body;  
```  

Then export each batch as a `.geojson` file.

### 7. Join the GeoJSON Files and Calculate Area (in Python)

Use a short Python script to:

- Load all `.geojson` files
- Reproject to British National Grid for accurate area calculation
- Compute area in m² and hectares
- Drop unneeded columns
- Export one file with just data and another with geometry for mapping

```python
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
```


### 8. Load the Datasets into Tableau

Bring both CSV files into Tableau:

- The original locations CSV
- The new boundaries CSV

Join them on the `@id` field.

### 9. Create Calculated Fields in Tableau

- **Google Maps GPS link**  
  ```  
  "https://maps.google.com/?q=" + STR([lat]) + "," + STR([lon])  
  ```  

- **OpenStreetMap object link**  
  ```  
  "https://www.openstreetmap.org/" + [id]  
  ```  

- **Create size classification (to colour code properties by size)**  
  ```
  IF ISNULL(SUM([Area M2])) THEN "No Data" // Catches NULLs first
  ELSEIF SUM([Area M2]) < 100000 THEN "Small"
  ELSEIF SUM([Area M2]) < 750000 THEN "Medium"
  ELSE "Large"
  END
  ```

### 10. Add Interactivity in the Dashboard

Include dashboard actions that:

- Allow users to search by business name
- Click on a site to open GPS or OSM links
- Filter by site size

---

## 🧰 Tools Used

- OpenStreetMap (Overpass Turbo)  
- GeoJSON.io  
- Excel  
- Python (GeoPandas) or R (sf, dplyr)  
- Tableau Desktop  

---

## 📌 Notes

- Rate limiting is a concern when querying Overpass. Keep batch sizes reasonable.  
- Names in OSM aren't standardized — some manual review or fuzzy matching may be helpful.  
- This process can be extended to retail parks, office clusters, brownfield sites, etc.  

---

## 🤝 Contributing

Pull requests are welcome if you want to improve the automation or generalize the pipeline.

---
