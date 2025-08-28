import os
import re
import sys
import numpy as np
import c3d
import pandas as pd



def _sanitize_labels(raw_labels, n_expected, prefix):
    # Trim to the number of available columns and fill empties
    labels = [str(l or "").strip() for l in raw_labels[:n_expected]]
    if len(labels) < n_expected:
        labels += ["" for _ in range(n_expected - len(labels))]
    labels = [labels[i] if labels[i] else f"{prefix}{i+1}" for i in range(n_expected)]
    return labels

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

def write_trc(markers_df, trc_file, units, frame_rate, first_frame):
    """
    Write marker data (frames, n_markers, 3) to TRC.
    """
    
    # remove time column
    time = markers_df["time"]
    markers_df = markers_df.drop(columns=["time"])
    
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

def write_mot(analog_df, labels, mot_file):
    """
    Write analog data (samples, n_channels) to MOT.
    
    inputs:
        labels: The labels for the analog channels.
        analog_df: The DataFrame containing the analog data.
        
    """
    
    # make sure labels include time
    labels = ['time'] + labels

    # Crop dataframe to include only labels
    analog_df = analog_df[labels]
    num_samples, num_columns = analog_df.shape
    
    # create writer
    with open(mot_file, "w") as writer:
        # Header
        writer.write(f"{os.path.basename(writer.name)}\n")
        writer.write("version=1\n")
        writer.write(f"nRows={num_samples}\n")
        writer.write(f"nColumns={num_columns}\n") 
        writer.write("in_degrees=yes\n")
        writer.write("endheader\n")

        # Column labels
        writer.write("\t".join(labels) + "\n")
    
        # Data rows
        for i, row in analog_df.iterrows():
            # breakpoint()
            writer.write(f"{row['time']:.6f}\t" + "\t".join([f"{val:.6f}" for val in row[1:]]) + "\n")

def main(c3d_filepath):
    print(f"Reading C3D file: {c3d_filepath}")
    try:
        reader = c3d.Reader(open(c3d_filepath, "rb"))
    except Exception as e:
        print(f"Error: Could not open or read the C3D file. {e}")
        return 1

    # Rates and frames
    marker_rate = float(reader.header.frame_rate)
    analog_rate = float(reader.header.frame_rate * reader.header.analog_per_frame)
    first_frame = int(reader.header.first_frame)
    num_frames = int(reader.frame_count)
    
    # Units (fallback to 'mm' if not available)
    units = "mm"

    # Labels, clamped to available columns to avoid index errors
    marker_labels = [str(l or "").strip() for l in reader.point_labels]
    analog_labels = [str(l or "").strip() for l in reader.analog_labels]

    # create time vector
    initial_time = first_frame / marker_rate
    final_time = (first_frame + num_frames-1) / marker_rate
    time = np.linspace(initial_time, final_time, num_frames)
    
    analog_df = pd.DataFrame(index=range(num_frames),columns=analog_labels)
    analog_df['time'] = time

    columns = pd.MultiIndex.from_tuples([(name, "") for name in marker_labels])
    # Create MultiIndex columns with X1, Y1, Z1, X2, Y2, Z2 etc. for each marker
    marker_columns = []
    for i, name in enumerate(marker_labels, 1):
        marker_columns.extend([(name, f'X{i}'), (name, f'Y{i}'), (name, f'Z{i}')])
    
    columns = pd.MultiIndex.from_tuples(marker_columns)
    marker_df = pd.DataFrame(index=range(num_frames), columns=columns)
    marker_df['time'] = time

    # move time to first column
    cols = analog_df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    analog_df = analog_df[cols]

    cols = marker_df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    marker_df = marker_df[cols]

    # Collect frames
    for frame_no, points, analog in reader.read_frames():
        # get row number and print loading bar
        i_row = frame_no - first_frame
        # convert analog data to list
        analog_list  = analog.data.tolist()
        # points: (n_points, 5) -> take XYZ
        marker_list = points[:, :3]

        # loop through analog channels and add to dataframe
        for i_channel in range(len(analog_list)):
            channel_name = analog_labels[i_channel]
            
            # add channel to dataframe
            analog_df.loc[i_row, channel_name] = analog[i_channel][0]

        # loop through marker channels and add to dataframe
        for i_marker in range(len(marker_list)):
            marker_name = marker_labels[i_marker]
            # Assign X, Y, Z coordinates separately or flatten the array
            marker_df.loc[i_row, marker_name] = marker_list[i_marker]   

    # save analog to csv
    analog_path = os.path.join(os.path.dirname(c3d_filepath), "analog.csv")
    analog_df.to_csv(analog_path, index=False)
    print(f"Successfully exported {analog_path}")

    # Write TRC
    trc_path = os.path.join(os.path.dirname(c3d_filepath), "markers.trc")
    write_trc(marker_df, trc_path, units, marker_rate, first_frame)
    
    # rotate marker df 90z and -90x
    rotated_marker_df= rotate_dataframe_columns(marker_df, angle_degrees=90, axis='z')
    rotated_marker_df= rotate_dataframe_columns(rotated_marker_df, angle_degrees=-90, axis='x')
    write_trc(rotated_marker_df, trc_path.replace('.trc', '_rotated_z_x.trc'), units, marker_rate, first_frame)
    print(f"Successfully exported {trc_path}")

    # Write GRF MOT
    grf_indices = [i for i, lbl in enumerate(analog_labels) if "force" in lbl.lower() or "moment" in lbl.lower()]
    breakpoint()
    if grf_indices:
        grf_labels = [analog_labels[i] for i in grf_indices]
        grf_mot_path = os.path.join(os.path.dirname(c3d_filepath), "grf.mot")
        write_mot(analog_df, grf_labels, grf_mot_path)
        print(f"Successfully exported {grf_mot_path}")
    else:
        print("Warning: No GRF channels found among available analog channels.")

    # Write EMG MOT
    emg_indices = [i for i, lbl in enumerate(analog_labels) if "emg" in lbl.lower()]
    if emg_indices:
        emg_mot_path = os.path.join(os.path.dirname(c3d_filepath), "emg.mot")
        emg_labels = [analog_labels[i] for i in emg_indices]
        write_mot(analog_df, emg_labels, emg_mot_path)
        print(f"Successfully exported {emg_mot_path}")
    else:
        print("Warning: No EMG channels found among available analog channels.")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = input("Enter the path to the C3D file: ").strip().strip("'\"")
    sys.exit(main(path))
