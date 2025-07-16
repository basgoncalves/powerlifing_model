import os
import numpy as np
import utils
import paths
import matplotlib.pyplot as plt
import msk_modelling_python as msk

groups = None #paths.JCF_Groups
summary = '3dsum' # sum, mean, 3dsum

folder1 = input("Enter the path to the first folder: ")
folder2 = input("Enter the path to the second folder: ")
save_path = input("Enter the path to save the comparison plot: ")

files_folder1 = [os.path.join(root, f)
                 for root, _, files in os.walk(folder1)
                    for f in files if f.endswith('.sto') or f.endswith('.mot')]
files_folder2 = [os.path.join(root, f)
                 for root, _, files in os.walk(folder2)
                    for f in files if f.endswith('.sto') or f.endswith('.mot')]

# check for all common files in both folders
common_files = set(os.path.basename(f) for f in files_folder1).intersection(set(os.path.basename(f) for f in files_folder2))

# breakpoint()                                    
for file in common_files:                                                                                
    print(f"Comparing file: {file}")
    file1 = os.path.join(folder1, file)
    file2 = os.path.join(folder2, file)
    
    # try to get groups from paths.plot_settings
    try:
        groups = paths.plot_settings['Groups'][os.path.splitext(os.path.basename(file))[0]]
        summary = paths.plot_settings['Summary'][os.path.splitext(os.path.basename(file))[0]]
    except KeyError:
        print(f"No groups found for file: {file}. Using default groups.")
        groups = None
        
    
    file_parent1 = os.path.basename(os.path.dirname(file1))
    file_parent2 = os.path.basename(os.path.dirname(file2))
    
    if not os.path.exists(file1) or not os.path.exists(file2):
        print(f"One or both files do not exist: {file1}, {file2}")
        continue
    
    file1_data = utils.load_any_data_file(file1)
    file2_data = utils.load_any_data_file(file2)

    # find common columns
    common_columns = set(file1_data.columns).intersection(set(file2_data.columns))
    if not common_columns:
        print("No common columns found between the two files.")

    # print the coluns not matched from both files
    file1_not_matched = set(file1_data.columns) - common_columns
    file2_not_matched = set(file2_data.columns) - common_columns
    if file1_not_matched:
        print(f"Columns in {file1} not matched: {file1_not_matched}")
    if file2_not_matched:
        print(f"Columns in {file2} not matched: {file2_not_matched}")

    # if groups is not None and summary is not None sum the groups and create new columns
    if groups is not None and summary is not None:    
        for group in groups:
            if summary == 'sum':
                # sum al the groups in groups[group]
                file1_data[group] = file1_data[groups[group]].sum(axis=1)
                file2_data[group] = file2_data[groups[group]].sum(axis=1)
                common_columns.add(group)
            elif summary == 'mean':
                # mean all the groups in groups[group]
                file1_data[group] = file1_data[groups[group]].mean(axis=1)
                file2_data[group] = file2_data[groups[group]].mean(axis=1)
                common_columns.add(group)
            elif summary == '3dsum':
                # 3d sum all the groups in groups[group]
                file1_data[group] = np.linalg.norm(file1_data[groups[group]].values, axis=1)
                file2_data[group] = np.linalg.norm(file2_data[groups[group]].values, axis=1)
                common_columns.add(group)
        
        common_columns = groups.keys() 

    # time normlaise the time column if it exist
    file1_data_normalized = msk.bops.time_normalise_df(file1_data)
    file2_data_normalized = msk.bops.time_normalise_df(file2_data)

    # calculate screen window size
    screen_size = utils.get_screen_size()

    # set figure size NXN common columns
    n = len(common_columns)
    ncols = int(np.ceil(np.sqrt(n)))
    nrows = int(np.ceil(n / ncols))
    fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(screen_size[0] / 100, screen_size[1] / 100))
    axs = axs.flatten()  # Flatten to 1D for easy indexing

    # Plot each common column as a separate subplot
    for i, col in enumerate(common_columns):
        if col == 'time':
            continue
        try:
            axs[i].plot(file1_data_normalized['time'], file1_data_normalized[col], label=f'{file1} - {col}', color='blue')
            axs[i].plot(file2_data_normalized['time'], file2_data_normalized[col], label=f'{file2} - {col}', color='orange')
            axs[i].set_title(f'{col}')
            axs[i].set_ylabel(col)
            axs[i].grid()
        except KeyError as e:
            print(f"Column '{col}' not found in one of the files: {e}")
            continue
            
        if i == 1:
            axs[i].legend([f'{file_parent1}', f'{file_parent2}'])
        
        if i == n - 1:
            axs[i].set_xlabel('Time')
        
    plt.tight_layout()

   
    save_path = os.path.join(save_path, f"{file}.png") 

    if save_path:
        plt.savefig(save_path)
        print(f"Plot saved to {save_path}")
        
    else:
        print("Plot not saved.")
        
    print("Plotting complete. Check the saved file for the comparison.")

        
        