import os
import numpy as np
import utils
import paths
import matplotlib.pyplot as plt


file1 = input("Enter the path to the first file: ")
file2 = input("Enter the path to the second file: ")

file_parent1 = os.path.basename(os.path.dirname(file1))
file_parent2 = os.path.basename(os.path.dirname(file2))

if not os.path.exists(file1) or not os.path.exists(file2):
    raise FileNotFoundError("One or both files do not exist.")
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
    axs[i].plot(file1_data['time'], file1_data[col], label=f'{file1} - {col}', color='blue')
    axs[i].plot(file2_data['time'], file2_data[col], label=f'{file2} - {col}', color='orange')
    axs[i].set_title(f'{col}')
    axs[i].set_ylabel(col)
    axs[i].grid()
    
    if i == 1:
        axs[i].legend([f'{file_parent1}', f'{file_parent2}'])
    
    if i == n - 1:
        axs[i].set_xlabel('Time')
    
plt.tight_layout()


# ask where to save the plot with a dialog
import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()  # Hide the root window
save_path = filedialog.asksaveasfilename(defaultextension=".png", title="Save Plot",
                                           filetypes=[("PNG files", "*.png"), ("All files", "*.*")])

if save_path:
    plt.savefig(save_path)
    print(f"Plot saved to {save_path}")
    
else:
    print("Plot not saved.")
    
plt.show()
    
    