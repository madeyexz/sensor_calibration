import numpy as np
import pandas as pd
import folium
import logging
import geopandas as gpd
from shapely.geometry import Point

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load the data
with np.load('data/2021051202_merged.npz') as npz_file:
    data = npz_file['data']

# Load Beijing boundary
beijing_boundary = gpd.read_file('geoJson/beijing.json')

# Convert DataFrame to GeoDataFrame
df = pd.DataFrame(data, columns=['id', 'value', 'longitude', 'latitude', 'timestamp'])
geometry = [Point(xy) for xy in zip(df['longitude'].astype(float), df['latitude'].astype(float))]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

# Spatial join with Beijing boundary
beijing_df = gpd.sjoin(gdf, beijing_boundary, predicate='within')

# Log the number of datapoints
logging.info(f"Total number of datapoints: {len(df)}")
logging.info(f"Number of datapoints in Beijing: {len(beijing_df)}")
logging.info(f"Percentage of points in Beijing: {(len(beijing_df)/len(df))*100:.2f}%")

# Create a map centered at Beijing's center
center_lat = 39.9042
center_lon = 116.4074
m = folium.Map(location=[center_lat, center_lon], zoom_start=10)

# Add Beijing boundary
folium.GeoJson(
    'geoJson/beijing.json',  # 您需要准备北京的 GeoJSON 文件
    name='Beijing Boundary',
    style_function=lambda x: {
        'fillColor': 'transparent',
        'color': 'blue',
        'weight': 2
    }
).add_to(m)

# Add points to the map
for idx, row in beijing_df.iterrows():
    folium.CircleMarker(
        location=[float(row['latitude']), float(row['longitude'])],
        radius=3,
        color='red',
        fill=True
    ).add_to(m)

# Add layer control
folium.LayerControl().add_to(m)

# Save the map
m.save('mapResult/map_beijing.html')
