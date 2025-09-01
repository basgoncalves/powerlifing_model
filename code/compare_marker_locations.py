import os
import tkinter as tk
from tkinter import filedialog
import pandas as pd
import numpy as np
import re
import utils
    
def load_trc(path=None, output=0):

    # find line with '#Frame' to skip the header
    try:
        with open(path, 'r') as file:
            for i, line in enumerate(file):
                if 'Frame#' in line:
                        break
    except:
        print(f"Error: Could not read the file at {path}. Please check the path and try again.")
        return None
        
    # read headers in line i
    try:
        with open(path, 'r') as file:
            headers = file.readlines()[i].strip().split('\t')
    except:
        print(f"Error: Could not read the file at {path}. Please check the path and try again.")
        return None

    # read data headers and merge 2 rows of header and sub header
    try:
        with open(path, 'r') as file:
            headers = file.readlines()[i].strip().split('\t')

        with open(path, 'r') as file:
            sub_headers = file.readlines()[i+1].strip().split('\t')
    except:
        print(f"Error: Could not read the file at {path}. Please check the path and try again.")
        return None

    # Keep first two empty for Frame# and Time
    sub_headers = [''] * 2 + sub_headers[2:]  

    # Combine header 
    for _,idx in zip(headers, range(len(headers))):
        if headers[idx] == '':
            headers[idx] = headers[idx-1]

    for _,idx in zip(headers, range(len(headers))):
        if sub_headers[idx] != '':
            headers[idx] = f"{headers[idx]}_{sub_headers[idx]}"


    # read the file into a pandas DataFrame, skipping the header
    try:
        data = pd.read_csv(path, sep= '\s+', header=i+1, index_col=False)
        # add the headers to the DataFrame above the data
        data.columns = headers
        
    except Exception as e:
        print(f"Error: Could not read the file at {path}. Please check the file format and try again.")
        print(f"Details: {e}")
        return None

    if output == 1: print(data.columns)

    return data



def load_sto_file(filepath):
    """
    Loads a .sto file into a pandas DataFrame.
    Assumes the file format from OpenSim.
    """
    with open(filepath, 'r') as f:
        # Find the line 'endheader'
        for i, line in enumerate(f):
            if 'endheader' in line:
                header_line = i + 1
                break
        else:
            raise ValueError("STO file 'endheader' not found.")

    # Read the data, skipping metadata
    df = pd.read_csv(filepath, sep='\t', header=header_line)
    # The first column is often 'time'
    df = df.rename(columns={'time': 'Time'})
    return df

def write_sto_file(data_df, filename):
    """
    Writes a pandas DataFrame to an OpenSim .sto file.
    """
    with open(filename, 'w') as f:
        f.write(f"{os.path.basename(filename)}\n")
        f.write(f"version=1\n")
        f.write(f"nRows={data_df.shape[0]}\n")
        f.write(f"nColumns={data_df.shape[1]}\n")
        f.write("inDegrees=yes\n")
        f.write("endheader\n")
        data_df.to_csv(f, sep='\t', index=False, lineterminator='\n')

def calculate_all_marker_errors(marker_experimental_path=None, marker_virtual_path=None):
    """
    Calculates the root mean square error between experimental and virtual markers.

    Args:
        marker_experimental_path (str, optional): Path to the experimental .trc file.
        marker_virtual_path (str, optional): Path to the virtual .sto markers file.
    """
    # Set up a root window for the file dialog but hide it
    root = tk.Tk()
    root.withdraw()

    # Select the trials if needed
    if not marker_experimental_path:
        marker_experimental_path = filedialog.askopenfilename(title='Select experimental .trc file', filetypes=[("TRC files", "*.trc")])
        if not marker_experimental_path: return # User cancelled

    if not marker_virtual_path:
        marker_virtual_path = filedialog.askopenfilename(title='Select virtual .sto markers file', filetypes=[("STO files", "*.sto")])
        if not marker_virtual_path: return # User cancelled

    virtual_markers_df = load_sto_file(marker_virtual_path)
    experimental_markers_df = load_trc(marker_experimental_path)

    marker_names = list([col.split('_')[0] for col in experimental_markers_df.columns if col != 'Time' and col != 'Frame#'])

    # Remove duplicates but keep same order
    marker_names = list(dict.fromkeys(marker_names))

    # Find frames to plot in the experimental data
    time = virtual_markers_df['Time']
    
    # Find the closest indices in experimental time to the start and end of virtual time
    exp_time = experimental_markers_df['Time']
    initial_index = (exp_time - time.iloc[0]).abs().idxmin()
    final_index = (exp_time - time.iloc[-1]).abs().idxmin()

    distances = pd.DataFrame({'Time': time.values})
    
    output_dir = os.path.dirname(marker_experimental_path)
    mean_errors_filename = os.path.join(output_dir, '_ik_marker_errors_mean.txt')

    print('Calculating marker errors for all markers...')
    with open(mean_errors_filename, 'w') as f_mean_errors:
        f_mean_errors.write('mean errors for each marker (m)\n\n')

        for marker_name in marker_names:
            try:
                
                marker_name = marker_name.split('_')[0]  # In case of multi-index, take the first part
                exp_cols = [col for col in experimental_markers_df.columns if col.split('_')[0] == marker_name]
                virtual_cols = [col for col in virtual_markers_df.columns if col.split('_')[0] == marker_name]
                
                # Get experimental data for the current time range and convert mm to m
                exp_slice = experimental_markers_df.iloc[initial_index:final_index + 1]
                x1 = exp_slice[exp_cols[0]].values / 1000.0
                y1 = exp_slice[exp_cols[1]].values / 1000.0
                z1 = exp_slice[exp_cols[2]].values / 1000.0

                # Get virtual data
                x2 = virtual_markers_df[virtual_cols[0]].values
                y2 = virtual_markers_df[virtual_cols[1]].values
                z2 = virtual_markers_df[virtual_cols[2]].values
                
                # Ensure arrays are the same length by trimming the longer one
                min_len = min(len(x1), len(x2))
                x1, y1, z1 = x1[:min_len], y1[:min_len], z1[:min_len]
                x2, y2, z2 = x2[:min_len], y2[:min_len], z2[:min_len]
                
                # Calculate the 3D distance
                dist = np.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
                distances[marker_name] = pd.Series(dist)

                # Write mean error to file
                mean_error_text = f'{marker_name} = {np.mean(dist):.4f} m\n'
                f_mean_errors.write(mean_error_text)

            except (KeyError, IndexError) as e:
                print(f"Could not process marker '{marker_name}'. It might be missing in one of the files. Error: {e}")

    # Write all distance data to a .sto file
    all_errors_filename = os.path.join(output_dir, '_ik_marker_errors_all.sto')
    write_sto_file(distances.dropna(axis=1, how='all'), all_errors_filename)
    print(f"Mean errors saved to: {mean_errors_filename}")
    print(f"All error data saved to: {all_errors_filename}")

if __name__ == '__main__':
    # Example of how to run the function.
    # If paths are not provided, file dialogs will open.
    calculate_all_marker_errors()