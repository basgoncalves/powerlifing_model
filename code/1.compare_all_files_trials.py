import os
import matplotlib
import numpy as np
import pandas as pd
import utils
import paths
import matplotlib.pyplot as plt
from collections import Counter
from typing import List, Set
from matplotlib.lines import Line2D

def get_folders_from_user() -> List[str]:
    """Continuously prompts the user for folder paths until an empty input is given."""
    folders = []
    print("--- Enter folder paths one by one. Press Enter on an empty line to finish. ---")
    while True:
        folder_path = input(f"Enter path for folder #{len(folders) + 1} (or press Enter to finish): ").strip().strip('"')
        if not folder_path:
            if len(folders) < 2:
                print("Error: At least two folders are required for comparison. Exiting.")
                exit()
            break
        if not os.path.isdir(folder_path):
            print(f"Warning: Directory not found at '{folder_path}'. Please try again.")
            continue
        folders.append(folder_path)
    print(f"--- {len(folders)} folders collected. Processing... ---\n")
    return folders

def find_files_to_plot(folder_paths: List[str]) -> Set[str]:
    """Finds files that exist in at least two of the provided folders."""
    if not folder_paths:
        return set()

    file_counter = Counter()
    for folder in folder_paths:
        try:
            # Create a set to count each file only once per folder
            files_in_folder = {f for f in os.listdir(folder) if f.endswith(('.sto', '.mot')) and os.path.isfile(os.path.join(folder, f))}
            file_counter.update(files_in_folder)
        except FileNotFoundError:
            print(f"Warning: Could not access folder: {folder}")
            continue
            
    # Return a set of filenames that appeared in 2 or more folders
    return {file for file, count in file_counter.items() if count >= 2}

def main():
    """Main execution function."""
    # 1. Get all folder paths from the user
    folder_paths = get_folders_from_user()
    save_directory = input("Enter the path to the directory to save comparison plots: ").strip().strip('"')

    if not os.path.isdir(save_directory):
        print(f"Save directory '{save_directory}' not found. Creating it.")
        os.makedirs(save_directory)

    # 2. Find all files that appear in at least two folders
    files_to_plot = find_files_to_plot(folder_paths)
    if not files_to_plot:
        print("No files were found in at least two of the specified folders. Exiting.")
        return
        
    print(f"\nFound {len(files_to_plot)} files to compare: {sorted(list(files_to_plot))}\n")
    labels = [os.path.basename(folder) for folder in folder_paths]

    # 3. Process each common file
    for file_basename in sorted(list(files_to_plot)):
        print(f"--- Comparing file: {file_basename} ---")
        
        # Load data if file exists, otherwise use an empty DataFrame as a placeholder
        data_list = []
        for folder in folder_paths:
            file_path = os.path.join(folder, file_basename)
            if os.path.exists(file_path):
                
                # Attempt to load the file, handle any exceptions
                try:
                    data_list.append(utils.load_any_data_file(file_path))
                except Exception as e:
                    print(f"Error loading file '{file_path}': {e}")
                    data_list.append(pd.DataFrame())
            else:
                data_list.append(pd.DataFrame()) # Add empty placeholder

        # Find common columns only among dataframes that are not empty
        non_empty_dfs = [df for df in data_list if not df.empty]
        if len(non_empty_dfs) < 2:
            print("Fewer than two valid data files found for this basename. Skipping.")
            continue
            
        common_cols = set(non_empty_dfs[0].columns)
        for df in non_empty_dfs[1:]:
            common_cols.intersection_update(set(df.columns))

        # Attempt to get grouping settings
        try:
            settings_key = os.path.splitext(file_basename)[0]
            groups = paths.plot_settings['Groups'][settings_key]
            summary = paths.plot_settings['Summary'][settings_key]
        except (AttributeError, KeyError):
            groups = None
            summary = None

        # If groups are defined, summarize and update common_cols
        if groups and summary:
            print(f"Applying '{summary}' grouping for '{settings_key}'")
            for df in data_list:
                if not df.empty: # Only process non-empty dataframes
                    for group_name, members in groups.items():
                        if summary == 'sum':
                            df[group_name] = df[members].sum(axis=1)
                        elif summary == 'mean':
                            df[group_name] = df[members].mean(axis=1)
                        elif summary == '3dsum':
                            df[group_name] = np.linalg.norm(df[members].values, axis=1)
            common_cols = set(groups.keys())
        
        # Time-normalize, keeping placeholders for empty dataframes
        normalized_data_list = [utils.time_normalise_df(df) if not df.empty else pd.DataFrame() for df in data_list]

        # Setup plot grid
        plot_cols = sorted([c for c in common_cols if c != 'time'])
        if not plot_cols:
            print(f"No data columns to plot for {file_basename}. Skipping.")
            continue
            
        n = len(plot_cols)
        ncols = int(np.ceil(np.sqrt(n)))
        nrows = int(np.ceil(n / ncols))
        fig, axs = plt.subplots(nrows, ncols, figsize=(5 * ncols, 4 * nrows), squeeze=False)
        axs = axs.flatten()
        plot_colors = matplotlib.colormaps['tab10'].colors

        # Plot each column on a separate subplot
        for i, col in enumerate(plot_cols):
            ax = axs[i]
            # Plot a line only if the dataframe is not an empty placeholder
            for j, norm_df in enumerate(normalized_data_list):
                if not norm_df.empty and col in norm_df.columns:
                    norm_time = np.linspace(0, 100, len(norm_df['time'])) 
                    ax.plot(norm_time, norm_df[col], color=plot_colors[j % len(plot_colors)])
            
            ax.set_title(col)
            ax.set_ylabel(col)
            ax.grid(True)
            if i >= n - ncols:
                ax.set_xlabel('Time (%)')

        # Create a complete, custom legend and add it to the last subplot
        legend_elements = [Line2D([0], [0], color=plot_colors[j % len(plot_colors)], lw=2, label=labels[j]) for j in range(len(labels))]
        # Place legend on the last available axis spot for better layout
        axs[len(axs)-1].legend(handles=legend_elements, loc='center')
        axs[len(axs)-1].axis('off') # Hide axis for the legend plot

        fig.suptitle(f'Comparison: {file_basename}', fontsize=16, weight='bold')
        plt.tight_layout(rect=[0, 0, 1, 0.96])

        # Save the plot
        output_filename = f"{os.path.splitext(file_basename)[0]}_comparison.png"
        output_filepath = os.path.join(save_directory, output_filename)
        plt.savefig(output_filepath, dpi=200)
        print(f"Plot saved to: {output_filepath}\n")
        plt.close(fig) # Close the figure to free up memory

    print("--- All comparisons complete. ---")

if __name__ == '__main__':
    main()