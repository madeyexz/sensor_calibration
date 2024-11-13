import numpy as np
import pandas as pd

def load_npz_to_dataframe(npz_file_path):
    """
    Load data from a .npz file into a pandas DataFrame
    
    Args:
        npz_file_path (str): Path to the .npz file
        
    Returns:
        pd.DataFrame: DataFrame containing the data from the .npz file
    """
    # Load the npz file
    data = np.load(npz_file_path)
    
    # Convert the arrays in the npz file to a dictionary
    # Flatten any multi-dimensional arrays
    data_dict = {}
    for key in data.files:
        arr = data[key]
        if arr.ndim > 1:
            # For 2D+ arrays, flatten them and create multiple columns
            for i in range(arr.shape[1]):
                data_dict[f"{key}_{i}"] = arr[:, i]
        else:
            data_dict[key] = arr
    
    # Create DataFrame from the dictionary
    df = pd.DataFrame(data_dict)
    
    return df

if __name__ == "__main__":
    df = load_npz_to_dataframe("data/2021051202_merged.npz")
    print(df.head())
    print(df.shape)
    print(df.keys())
