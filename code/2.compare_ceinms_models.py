import os
import numpy as np
import utils
import paths
import matplotlib.pyplot as plt

file1 = input("Enter the path to the FIRST ceinms model: ").replace('"', '')
file2 = input("Enter the path to the SECOND ceinms model: ").replace('"', '')

file_parent1 = os.path.basename(file1)
file_parent2 = os.path.basename(file2)

print(f"Comparing models: {file_parent1} vs {file_parent2}")

subject1 = utils.read_xml(file1)
subject2 = utils.read_xml(file2)

mtuSet1 = subject1.find('mtuSet')
mtuSet2 = subject2.find('mtuSet')

if mtuSet1 is None or mtuSet2 is None:
    raise ValueError("One or both models do not contain a muscleSet.")

n_muscles = len(mtuSet1.findall('mtu'))
# find all the elements in the first mtu
params = [element.tag for element in mtuSet1.find('mtu')]

# remove 'name' from the list of parameters
params = [param for param in params if param != 'name']

# create a figure for plotting with a subplot for each parameter
screen_size = utils.get_screen_size()
n = len(params)
ncols = int(np.ceil(np.sqrt(n)))
nrows = int(np.ceil(n / ncols))

fig, axs = plt.subplots(nrows=nrows, ncols=ncols, figsize=(screen_size[0] / 100, screen_size[1] / 100))
axs = axs.flatten()  # Flatten to 1D for easy indexing

# Calculate the last row index for the x-axis label
last_row_indices = list(range(ncols * (nrows - 1), ncols * nrows))

# loop through all the MTUs in the first model
for i, name in enumerate(params):
    if name == 'name':
        continue  # Skip the 'name' element
    
    print(f"Comparing parameter: {name}")
    
    values1 = [float(mtu.find(name).text) for mtu in mtuSet1.findall('mtu')]
    values2 = [float(mtu.find(name).text) for mtu in mtuSet2.findall('mtu')]

    # plot the values as a bar chart
    axs[i].bar(np.arange(n_muscles) - 0.2, values1, width=0.4, label=file_parent1, color='blue')
    axs[i].bar(np.arange(n_muscles) + 0.2, values2, width=0.4, label=file_parent2, color='orange')  
    axs[i].set_title(name)
    
    if i == 0:
        axs[i].legend([file_parent1, file_parent2])
    
    if i in last_row_indices:
    
        axs[i].set_xlabel('Muscle')
        axs[i].set_xticks(np.arange(n_muscles))
        axs[i].set_xticklabels([mtu.find('name').text for mtu in mtuSet1.findall('mtu')], rotation=90)
        
        
plt.tight_layout()
plt.show()