import os
import pandas as pd

import scipy.io as sio

def read_mat_and_save_csv(mat_file_path, output_dir=None):
    """
    Read a .mat file and save its contents as CSV file(s).
    
    Args:
        mat_file_path: Path to the .mat file
        output_dir: Directory to save CSV files (defaults to same directory as .mat file)
    """
    if output_dir is None:
        output_dir = os.path.dirname(mat_file_path)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Load the .mat file
    mat_data = sio.loadmat(mat_file_path)
    
    # Remove metadata keys (starting with __)
    mat_data = {k: v for k, v in mat_data.items() if not k.startswith('__')}
    
    # Save each variable as a separate CSV file
    for key, value in mat_data.items():
        try:
            df = pd.DataFrame(value)
            csv_file_path = os.path.join(output_dir, f"{key}.csv")
            df.to_csv(csv_file_path, index=False)
            print(f"Saved: {csv_file_path}")
        except Exception as e:
            print(f"Could not save {key}: {e}")

if __name__ == "__main__":
    # Example usage
    mat_file = input("Enter the path to the .mat file: ").strip('"')
    read_mat_and_save_csv(mat_file)