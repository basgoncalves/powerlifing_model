"""
Compare multiple data files by loading them, finding common columns,
and plotting them in a single figure. The script allows users to select files,
summarize groups of columns, and visualize the data in a grid layout.
"""

import os
import numpy as np
import utils
import paths
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import filedialog
from typing import List, Dict, Any, Set
import pandas as pd

def get_files_from_user() -> List[str]:
    """Continuously prompts the user for file paths until an empty input is given."""
    files = []
    print("--- Enter file paths one by one. Press Enter on an empty line to finish. ---")
    while True:
        file_path = input(f"Enter path for file #{len(files) + 1} (or press Enter to finish): ")
        if not file_path:
            if not files:
                print("No files were entered. Exiting.")
                exit()
            break
        
        # Optional: Handle quoted paths from drag-and-drop
        file_path = file_path.strip().strip('"')

        if not os.path.exists(file_path):
            print(f"Warning: File not found at '{file_path}'. Please try again.")
            continue
        files.append(file_path)
    print(f"--- {len(files)} files collected. Processing... ---")
    return files

def find_common_columns(dataframes: List[pd.DataFrame]) -> Set[str]:
    """Finds the set of column names common to all dataframes in a list."""
    if not dataframes:
        return set()
    
    # Start with columns of the first dataframe
    common = set(dataframes[0].columns)
    
    # Find the intersection with the columns of all other dataframes
    for df in dataframes[1:]:
        common.intersection_update(set(df.columns))
        
    return common

# --- Main Script Execution ---

# 1. Get all file paths from the user
file_paths = get_files_from_user()
first_file = file_paths[0]

# 2. Load plot settings based on the *first* file
try:
    file_basename = os.path.splitext(os.path.basename(first_file))[0]
    groups = paths.Settings().plot['Groups'][file_basename]
    summary = paths.Settings().plot['Summary'][file_basename]
    print(f"Using plot settings for '{file_basename}' with summary method: '{summary}'.")
except KeyError:
    print(f"No specific plot settings found for: {first_file}. Using default columns.")
    groups = None
    summary = None

# 3. Load all data files into a list of dataframes
data_list = [utils.load_any_data_file(fp) for fp in file_paths]

# 4. Find common columns across all files
common_columns = find_common_columns(data_list)

if not common_columns:
    raise ValueError("No common columns found among the specified files. Cannot compare.")

# 5. Report columns that are not matched for each file
print("\n--- Column Matching Report ---")
for i, df in enumerate(data_list):
    unmatched_cols = set(df.columns) - common_columns
    if unmatched_cols:
        print(f"Columns in '{os.path.basename(file_paths[i])}' not in common set: {unmatched_cols}")
print("----------------------------\n")


# 6. If groups are defined, summarize them for each dataframe
if groups is not None and summary is not None:
    for df in data_list:  # Loop through each dataframe
        for group_name, member_cols in groups.items():
            if summary == 'Sum':
                df[group_name] = df[member_cols].sum(axis=1)
            elif summary == 'mean':
                df[group_name] = df[member_cols].mean(axis=1)
            elif summary == '3dsum':
                df[group_name] = np.linalg.norm(df[member_cols].values, axis=1)
    
    # After summarizing, the common columns are the new group keys
    common_columns = groups.keys()

# 7. Time-normalize each dataframe
normalized_data_list = []
for df in data_list:
    if not df.empty:
        normalized_df = utils.time_normalise_df(df)
        normalized_data_list.append(normalized_df)
    else:
        print(f"Warning: DataFrame for '{os.path.basename(file_paths[data_list.index(df)])}' is empty. Skipping normalization.")
        normalized_data_list.append(pd.DataFrame())  # Append an empty DataFrame for consistency

# 8. Setup the plot figure
screen_size = utils.get_screen_size()
n_plots = len(common_columns) - 1 if 'time' in common_columns else len(common_columns)
if n_plots <= 0:
    raise ValueError("No data columns to plot after processing.")

ncols = int(np.ceil(np.sqrt(n_plots)))
nrows = int(np.ceil(n_plots / ncols))
fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(screen_size[0] / 100, screen_size[1] / 100), squeeze=False)
axs = axs.flatten()  # Flatten to 1D for easy indexing
plot_colors = plt.cm.get_cmap('tab10', 10).colors # Get a set of distinct colors

labels = utils.get_unique_names(file_paths)

# 9. Plot each common column on a separate subplot
plot_idx = 0
for col in sorted(list(common_columns)): # Sort for consistent plot order
    if col == 'time':
        continue
    
    ax = axs[plot_idx]
    
    # Plot data from each file on the current subplot
    for i, norm_df in enumerate(normalized_data_list):
        try:
            time_vector = utils.np.linspace(0, 100, len(norm_df['time'])) 
            ax.plot(time_vector, norm_df[col], color=plot_colors[i % len(plot_colors)], label=labels[i])
        except KeyError:
            print(f"Warning: Column '{col}' unexpectedly not found in normalized data from '{os.path.basename(file_paths[i])}'. Skipping.")
            continue
            
    ax.set_title(col)
    ax.set_ylabel(col)
    ax.grid(True)

    if plot_idx == 0:
        ax.legend()
        
    if plot_idx >= n_plots - ncols: # Set xlabel for the bottom row plots
        ax.set_xlabel('Time (%)')

    plot_idx += 1

# Hide any unused subplots
for i in range(plot_idx, len(axs)):
    axs[i].set_visible(False)

plt.tight_layout()

# 10. Ask user where to save the plot
root = tk.Tk()
root.withdraw()  # Hide the root window
root.attributes('-topmost', True) # Bring dialog to front

save_path = filedialog.asksaveasfilename(
    defaultextension=".png", 
    title="Save Comparison Plot",
    filetypes=[("PNG files", "*.png"), ("SVG files", "*.svg"), ("All files", "*.*")]
)

if save_path:
    plt.savefig(save_path, dpi=300)
    print(f"Plot saved to {save_path}")
else:
    print("Save operation cancelled. Showing plot instead.")
    plt.show()

print("\nPlotting complete.")