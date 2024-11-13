import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import logging
import os
from tqdm import tqdm
import gc
from multiprocessing import Pool, cpu_count

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='processing.log'
)

def process_single_file(args):
    file_path, beijing_boundary_path = args
    try:
        # Load Beijing boundary for each process
        beijing_boundary = gpd.read_file(beijing_boundary_path)
        
        with np.load(file_path, mmap_mode='r') as npz_file:
            data = npz_file['data']
            chunk_size = 1_000_000
            heights = []
            
            for i in range(0, len(data), chunk_size):
                chunk = data[i:i + chunk_size]
                df_chunk = pd.DataFrame(chunk, columns=['id', 'value', 'longitude', 'latitude', 'timestamp'])
                df_chunk['value'] = pd.to_numeric(df_chunk['value'], errors='coerce')
                geometry = [Point(xy) for xy in zip(df_chunk['longitude'].astype(float), 
                                                  df_chunk['latitude'].astype(float))]
                gdf_chunk = gpd.GeoDataFrame(df_chunk, geometry=geometry, crs="EPSG:4326")
                beijing_chunk = gpd.sjoin(gdf_chunk, beijing_boundary, predicate='within')
                heights.extend(beijing_chunk['value'].tolist())
                
                del df_chunk, gdf_chunk, beijing_chunk
                gc.collect()
        
        logging.info(f"Processed {file_path}")
        return heights
    except Exception as e:
        logging.error(f"Error processing {file_path}: {str(e)}")
        return []

def main():
    # Set up number of processes (leave some cores free for system operations)
    num_processes = cpu_count() - 2  # Using 38 cores out of 40
    
    # data_dir = '/mnt/cyy14/2021_hourly_merged_moji_data_in_China' # file location in lab server
    data_dir = 'data' # file location in local
    beijing_boundary_path = 'geoJson/beijing.json'
    
    # Prepare arguments for multiprocessing
    npz_files = [f for f in os.listdir(data_dir) if f.endswith('.npz')]
    process_args = [(os.path.join(data_dir, f), beijing_boundary_path) for f in npz_files]
    
    # Process files in parallel
    all_heights = []
    with Pool(processes=num_processes) as pool:
        for heights in tqdm(
            pool.imap_unordered(process_single_file, process_args),
            total=len(npz_files),
            desc="Processing files"
        ):
            all_heights.extend(heights)
            
    # Create histogram from all collected heights
    plt.figure(figsize=(12, 6))
    n_bins = int(np.ceil(np.log2(len(all_heights))) + 1)
    counts, bins, patches = plt.hist(all_heights, bins=n_bins, edgecolor='black')
    
    # Add count labels on top of each bar
    for i in range(len(counts)):
        plt.text(bins[i] + (bins[1]-bins[0])/2, counts[i], 
                 f'{int(counts[i])}', 
                 ha='center', va='bottom')

    plt.xlabel('Height Value (m)')
    plt.ylabel('Number of Data Points')
    plt.title(f'Distribution of Height Values in Beijing')
    plt.grid(True, alpha=0.3)

    # Add mean and median lines
    mean_height = np.mean(all_heights)
    median_height = np.median(all_heights)
    plt.axvline(mean_height, color='red', linestyle='dashed', label=f'Mean: {mean_height:.1f}m')
    plt.axvline(median_height, color='green', linestyle='dashed', label=f'Median: {median_height:.1f}m')
    plt.legend(title=f'Total Points: {len(all_heights):,}')

    # Log statistics
    logging.info(f"Number of bins: {n_bins}")
    logging.info(f"Bin width: {(max(all_heights) - min(all_heights)) / n_bins:.2f} meters")
    logging.info(f"Min height: {min(all_heights):.2f} meters")
    logging.info(f"Max height: {max(all_heights):.2f} meters")
    logging.info(f"Mean height: {mean_height:.2f} meters")
    logging.info(f"Median height: {median_height:.2f} meters")

    # Save the plot
    plt.savefig('plotResults/height_distribution.png')
    plt.close()

if __name__ == "__main__":
    main()