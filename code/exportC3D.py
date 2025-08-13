import os
import sys
import numpy as np
import c3d


def _sanitize_labels(raw_labels, n_expected, prefix):
    # Trim to the number of available columns and fill empties
    labels = [str(l or "").strip() for l in raw_labels[:n_expected]]
    if len(labels) < n_expected:
        labels += ["" for _ in range(n_expected - len(labels))]
    labels = [labels[i] if labels[i] else f"{prefix}{i+1}" for i in range(n_expected)]
    return labels


def write_trc(writer, markers, marker_labels, frame_rate, first_frame, units):
    """
    Write marker data (frames, n_markers, 3) to TRC.
    """
    num_frames = markers.shape[0]
    n_markers = markers.shape[1]
    last_frame = first_frame + num_frames - 1

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
    writer.write("\n")

    # Data rows
    for i, frame in enumerate(markers):
        frame_num = first_frame + i
        time = i / frame_rate  # Start time at 0.0
        row = [f"{frame_num}", f"{time:.6f}"]
        row.extend([f"{coord:.6f}" for coord in frame.reshape(-1)])
        writer.write("\t".join(row) + "\n")


def write_mot(writer, labels, data, rate, file_type_name):
    """
    Write analog data (samples, n_channels) to MOT.
    """
    if data.ndim != 2:
        data = data.reshape(data.shape[0], -1)

    num_samples, num_columns = data.shape

    # Header
    writer.write(f"{os.path.basename(writer.name)}\n")
    writer.write("version=1\n")
    writer.write(f"nRows={num_samples}\n")
    writer.write(f"nColumns={num_columns + 1}\n")  # +1 for time
    writer.write("in_degrees=yes\n")
    writer.write("endheader\n")

    # Column labels
    writer.write("time\t" + "\t".join(labels) + "\n")

    # Data rows
    for i, sample in enumerate(data):
        time = i / rate
        row = [f"{time:.6f}"] + [f"{val:.6f}" for val in sample]
        writer.write("\t".join(row) + "\n")


def main(c3d_filepath):
    print(f"Reading C3D file: {c3d_filepath}")
    try:
        reader = c3d.Reader(open(c3d_filepath, "rb"))
    except Exception as e:
        print(f"Error: Could not open or read the C3D file. {e}")
        return 1

    # Collect frames
    marker_frames = []
    analog_frames = []  # list of (analog_per_frame, n_channels)

    for frame_no, points, analog in reader.read_frames():
        # points: (n_points, 5) -> take XYZ
        marker_frames.append(points[:, :3])
        # analog: (analog_per_frame, n_channels)
        analog_frames.append(analog)

    if not marker_frames:
        print("Error: No frames found.")
        return 1

    markers = np.asarray(marker_frames)  # (n_frames, n_markers, 3)
    analog_all = np.vstack(analog_frames)  # (n_frames*analog_per_frame, n_channels)

    # Rates and frames
    marker_rate = float(reader.header.frame_rate)
    analog_rate = float(reader.header.frame_rate * reader.header.analog_per_frame)
    first_frame = int(reader.header.first_frame)

    # Units (fallback to 'mm' if not available)
    units = "mm"

    # Labels, clamped to available columns to avoid index errors
    marker_labels_raw = [str(l or "").strip() for l in reader.point_labels]
    marker_labels = _sanitize_labels(marker_labels_raw, markers.shape[1], "Marker")

    analog_labels = [str(l or "").strip() for l in reader.analog_labels]

    # Write TRC
    trc_path = os.path.join(os.path.dirname(c3d_filepath), "markers.trc")
    with open(trc_path, "w") as f:
        write_trc(f, markers, marker_labels, marker_rate, first_frame, units)
    print(f"Successfully exported {trc_path}")

    # Identify GRF and EMG channels (within available columns only)
    grf_indices = [i for i, lbl in enumerate(analog_labels) if "force" in lbl.lower() or "moment" in lbl.lower()]
    emg_indices = [i for i, lbl in enumerate(analog_labels) if "emg" in lbl.lower()]
    

    # Export GRF
    if grf_indices:
        grf_data = analog_all[grf_indices, :]
        grf_labels = [analog_labels[i] for i in grf_indices]
        grf_path = os.path.join(os.path.dirname(c3d_filepath), "grf.mot")
        with open(grf_path, "w") as f:
            write_mot(f, grf_labels, grf_data, analog_rate, "Ground Reaction Forces")
        print(f"Successfully exported {grf_path}")
    else:
        print("Warning: No GRF channels found among available analog channels.")

    # Export EMG
    if emg_indices:
        emg_data = analog_all[emg_indices, :]
        emg_labels = [analog_labels[i] for i in emg_indices]
        emg_path = os.path.join(os.path.dirname(c3d_filepath), "emg.mot")
        with open(emg_path, "w") as f:
            write_mot(f, emg_labels, emg_data, analog_rate, "EMG Signals")
        print(f"Successfully exported {emg_path}")
    else:
        print("Warning: No EMG channels found among available analog channels.")

    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = input("Enter the path to the C3D file: ").strip().strip("'\"")
    sys.exit(main(path))
