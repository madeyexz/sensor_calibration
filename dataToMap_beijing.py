import numpy as np
import pandas as pd
import folium
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Load the data
with np.load('data/2021051202_merged.npz') as npz_file:
    data = npz_file['data']

# Define Beijing's approximate boundaries
BEIJING_BOUNDS = {
    'lat_min': 39.4,
    'lat_max': 41.0,
    'lon_min': 115.7,
    'lon_max': 117.4
}

# Filter data for Beijing
df = pd.DataFrame(data, columns=['id', 'value', 'longitude', 'latitude', 'timestamp'])
beijing_df = df[
    (df['latitude'].astype(float) >= BEIJING_BOUNDS['lat_min']) &
    (df['latitude'].astype(float) <= BEIJING_BOUNDS['lat_max']) &
    (df['longitude'].astype(float) >= BEIJING_BOUNDS['lon_min']) &
    (df['longitude'].astype(float) <= BEIJING_BOUNDS['lon_max'])
]

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
m.save('map_beijing.html')
