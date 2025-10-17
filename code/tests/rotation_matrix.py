import os
import pandas as pd
import numpy as np
import re

def rotate_dataframe_columns(df, angle_degrees, axis):
    """
    Applies a 3D rotation to all x, y, and z columns of a pandas DataFrame.
    The function automatically identifies the columns based on a naming convention.

    Args:
        df (pd.DataFrame): The input DataFrame.
        angle_degrees (float): The rotation angle in degrees.
        axis (str): The axis of rotation ('x', 'y', or 'z').
    
    Returns:
        pd.DataFrame: A new DataFrame with the rotated values.
    """
    rotated_df = df.copy()
    theta = np.deg2rad(angle_degrees)

    # Define the rotation matrix based on the specified axis
    if axis == 'x':
        rotation_matrix = np.array([
            [1, 0, 0],
            [0, np.cos(theta), -np.sin(theta)],
            [0, np.sin(theta), np.cos(theta)]
        ])
    elif axis == 'y':
        rotation_matrix = np.array([
            [np.cos(theta), 0, np.sin(theta)],
            [0, 1, 0],
            [-np.sin(theta), 0, np.cos(theta)]
        ])
    elif axis == 'z':
        rotation_matrix = np.array([
            [np.cos(theta), -np.sin(theta), 0],
            [np.sin(theta), np.cos(theta), 0],
            [0, 0, 1]
        ])
    else:
        raise ValueError("Invalid axis. Choose 'x', 'y', or 'z'.")

    # Automatically identify and group the x, y, z columns
    # We will use a dictionary to group columns by their top-level name
    columns_to_rotate_dict = {}

    # Check for both single-level and multi-level columns
    if isinstance(df.columns, pd.MultiIndex):
        # Multi-level columns: ('Bar:BL', 'X1'), ('Bar:BL', 'Y1'), etc.
        for col_tuple in df.columns:
            top_level = col_tuple[0]
            sub_level = col_tuple[1]
            if re.match(r'[XYZ]\d+', sub_level, re.IGNORECASE):
                if top_level not in columns_to_rotate_dict:
                    columns_to_rotate_dict[top_level] = {}
                columns_to_rotate_dict[top_level][sub_level] = col_tuple
    else:
        # Single-level columns: 'X1', 'Y1', 'Z1', etc.
        for col in df.columns:
            if re.match(r'[XYZ]\d+', col, re.IGNORECASE):
                # The group name is the part of the string before the 'X', 'Y', or 'Z'
                group_name = re.split(r'[XYZ]', col)[0]
                if group_name not in columns_to_rotate_dict:
                    columns_to_rotate_dict[group_name] = {}
                columns_to_rotate_dict[group_name][col] = col

    # Iterate through the grouped columns and apply the rotation
    for group_name, cols in columns_to_rotate_dict.items():
        # Ensure we have all three coordinates
        x_col = next((v for k, v in cols.items() if 'X' in str(k).upper()), None)
        y_col = next((v for k, v in cols.items() if 'Y' in str(k).upper()), None)
        z_col = next((v for k, v in cols.items() if 'Z' in str(k).upper()), None)

        if x_col and y_col and z_col:
            # Create a temporary DataFrame or array of the coordinates
            coords = rotated_df[[x_col, y_col, z_col]].values

            # Apply the rotation
            rotated_coords = np.dot(coords, rotation_matrix.T)

            # Update the DataFrame with the new rotated values
            rotated_df[[x_col, y_col, z_col]] = rotated_coords
        else:
            print(f"Warning: Group '{group_name}' is missing one or more 'x', 'y', or 'z' columns and will be skipped.")
    
    return rotated_df

def load_data_from_file(file_path, header_rows=3):
    """
    Loads data from a .trc file or similar format with two header rows.
    """
    # The first two rows often contain metadata, with the third being the column names
    # We use a MultiIndex to correctly handle the nested column structure
    df = pd.read_csv(file_path, sep='\t', header=[0, 1, 2])
    return df



def write_trc(markers_df, trc_file, units, frame_rate, first_frame):
    """
    Write marker data (frames, n_markers, 3) to TRC.
    """
    
    # remove time column
    time = markers_df["Time"]
    markers_df = markers_df.drop(columns=["Time"])

    num_frames = markers_df.shape[0]
    marker_labels = markers_df.columns.droplevel(1).to_list()
    
    # only unique labels
    marker_labels = list(dict.fromkeys(marker_labels))
    n_markers = len(marker_labels)

    with open(trc_file, "w") as writer:
        # Header
        writer.write(f"PathFileType\t4\t(X/Y/Z)\t{os.path.basename(writer.name)}\n")
        writer.write("DataRate\tCameraRate\tNumFrames\tNumMarkers\tUnits\tOrigDataRate\tOrigDataStartFrame\tOrigNumFrames\n")
        writer.write(f"{frame_rate}\t{frame_rate}\t{num_frames}\t{n_markers}\t{units}\t{frame_rate}\t{first_frame}\t{num_frames}\n")

        # Marker names
        header = "Frame#\tTime\t" + "\t".join([f"{name}\t\t" for name in marker_labels]) + "\n"
        writer.write(header)

        # Coordinate labels
        coord_line = "\t\t" + "\t".join([f"X{i+1}\tY{i+1}\tZ{i+1}" for i in range(n_markers)]) + "\n"
        writer.write(coord_line)

        # Data rows
        for i in range(num_frames):
            frame_num = first_frame + i
            time_val = time.iloc[i]
            row = [f"{frame_num}", f"{time_val:.6f}"]
            row.extend([f"{coord:.6f}" for coord in markers_df.iloc[i].values])
            writer.write("\t".join(row) + "\n")



# --- Example Usage ---

# Create a sample DataFrame that mimics your file structure
# In a real scenario, you would load this from your .trc file
# For example: df = load_data_from_file('your_file.trc')

data = {
    ('Unnamed: 1_level_0', 'Time_level_1'): [2.655, 2.66],
    ('VerticeA', 'X1'): [0.0, 0.0],
    ('VerticeA', 'Y1'): [0.0, 0.0],
    ('VerticeA', 'Z1'): [0.0, 0.0],
    ('VerticeB', 'X2'): [100.0, 100.0],
    ('VerticeB', 'Y2'): [0.0, 0.0],
    ('VerticeB', 'Z2'): [0.0, 0.0],
    ('VerticeC', 'X3'): [50.0, 50.0],
    ('VerticeC', 'Y3'): [86.6, 86.6],
    ('VerticeC', 'Z3'): [0.0, 0.0]
}
# Create a MultiIndex for a clean example
df = pd.DataFrame(data)
df.columns = pd.MultiIndex.from_tuples([
    ('Time', ''),
    ('VerticeA', 'X1'), ('VerticeA', 'Y1'), ('VerticeA', 'Z1'), 
    ('VerticeB', 'X2'), ('VerticeB', 'Y2'), ('VerticeB', 'Z2'),
    ('VerticeC', 'X3'), ('VerticeC', 'Y3'), ('VerticeC', 'Z3')
])



breakpoint()
# Perform a 90-degree rotation around the Z-axis
rotated_df = rotate_dataframe_columns(df, angle_degrees=90, axis='y')

# save both data frames
write_trc(df, 'original_data.trc', units='mm', frame_rate=100, first_frame=531)
write_trc(rotated_df, 'rotated_data.trc', units='mm', frame_rate=100, first_frame=531)