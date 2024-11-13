import numpy as np
import pandas as pd
import folium

# Load the data
with np.load('data/2021051202_merged.npz') as npz_file:
    data = npz_file['data']

# Convert to DataFrame with meaningful column names
df = pd.DataFrame(data, columns=['id', 'value', 'longitude', 'latitude', 'timestamp'])

# Create a map centered at the mean coordinates
center_lat = df['latitude'].astype(float).mean()
center_lon = df['longitude'].astype(float).mean()
m = folium.Map(location=[center_lat, center_lon], zoom_start=10)

# Add points to the map
for idx, row in df.iterrows():
    folium.CircleMarker(
        location=[float(row['latitude']), float(row['longitude'])],
        radius=3,
        color='red',
        fill=True
    ).add_to(m)

# Save the map
m.save('map.html')
