import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import logging

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
# Convert 'value' column to float
df['value'] = pd.to_numeric(df['value'], errors='coerce')
geometry = [Point(xy) for xy in zip(df['longitude'].astype(float), df['latitude'].astype(float))]
gdf = gpd.GeoDataFrame(df, geometry=geometry, crs="EPSG:4326")

# Spatial join with Beijing boundary
beijing_df = gpd.sjoin(gdf, beijing_boundary, predicate='within')

# Calculate histogram bins
min_height = beijing_df['value'].min()
max_height = beijing_df['value'].max()
# Use Sturges' rule to determine number of bins
n_bins = int(np.ceil(np.log2(len(beijing_df))) + 1)
bins = np.linspace(min_height, max_height, n_bins)

# Create histogram
plt.figure(figsize=(12, 6))
plt.hist(beijing_df['value'], bins=bins, edgecolor='black')
plt.xlabel('Height Value (m)')
plt.ylabel('Number of Data Points')
plt.title('Distribution of Height Values in Beijing')
plt.grid(True, alpha=0.3)

# Add mean and median lines
mean_height = beijing_df['value'].mean()
median_height = beijing_df['value'].median()
plt.axvline(mean_height, color='red', linestyle='dashed', label=f'Mean: {mean_height:.1f}m')
plt.axvline(median_height, color='green', linestyle='dashed', label=f'Median: {median_height:.1f}m')
plt.legend()

# Log statistics
logging.info(f"Number of bins: {n_bins}")
logging.info(f"Bin width: {(max_height - min_height) / n_bins:.2f} meters")
logging.info(f"Min height: {min_height:.2f} meters")
logging.info(f"Max height: {max_height:.2f} meters")
logging.info(f"Mean height: {mean_height:.2f} meters")
logging.info(f"Median height: {median_height:.2f} meters")

# Save the plot
plt.savefig('mapResult/height_distribution.png')
plt.close()
