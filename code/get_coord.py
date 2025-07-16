import opensim
import paths

# 1. Define the path to your motion file
mot_filepath = paths.IK_OUTPUT

# 2. Load the .mot file into a TimeSeriesTable
# The TimeSeriesTable constructor directly accepts the file path.
table = opensim.TimeSeriesTable(mot_filepath)

# 3. Get the coordinate names (column labels)
# This returns a Python list of strings.
coord_names = table.getColumnLabels()

# 4. Get the time vector
# This returns the independent column (time) as a NumPy array.
time = table.getIndependentColumn()

# 5. Get the data matrix
# This returns all data columns as a NumPy matrix.
# Each column corresponds to a coordinate in 'coord_names'.
data_matrix = table.getMatrix().to_numpy()

# --- You now have all the data. Here's how to use it: ---

print(f"File loaded: {mot_filepath}")
print(f"Number of coordinates: {len(coord_names)}")
print(f"Number of time steps: {len(time)}")
print("\nCoordinates found:")
print(coord_names)

# Example: Print the value of the first coordinate at the first time step
first_coord_name = coord_names[0]
first_coord_value = data_matrix[0, 0] # matrix[row_index, column_index]
print(f"\nValue of '{first_coord_name}' at time {time[0]:.2f}s is {first_coord_value:.4f}")

# Example: Get the entire time series for a specific coordinate
try:
    # Find the index of the coordinate you're interested in
    knee_angle_index = coord_names.index('knee_angle_r')
    # Get the entire column for that coordinate
    knee_angle_values = data_matrix[:, knee_angle_index]
    print(f"\nSuccessfully extracted all {len(knee_angle_values)} values for 'knee_angle_r'.")
except ValueError:
    print("\nCould not find 'knee_angle_r' in the coordinates.")
