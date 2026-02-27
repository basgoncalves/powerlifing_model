import c3d
import numpy as np

def get_events_from_c3d(file_path):
    """
    Extracts events and their times from a C3D file.

    Args:
        file_path (str): Path to the C3D file.

    Returns:
        List of tuples: (event_label, event_time)
    """
    events = []
    with open(file_path, 'rb') as handle:
        reader = c3d.Reader(handle)
        # Get frame rate for time calculation
        frame_rate = reader.header.frame_rate
        # Events are stored in parameters under 'EVENT'
        if 'EVENT' in reader.get('parameters'):
            event_params = reader.get('parameters')['EVENT']
            labels = event_params['LABELS'].string_array
            contexts = event_params['CONTEXTS'].string_array
            times = event_params['TIMES'].float_array  # shape: (2, n_events)
            used = event_params['USED'].integer_value
            for i in range(used):
                label = labels[i].strip()
                context = contexts[i].strip()
                # times[0, i] is the frame, times[1, i] is the time in seconds
                event_time = times[1, i]
                events.append((f"{context} {label}".strip(), event_time))
    return events

def calculate_trial_events_from_mot(mot_file_path=None, joint_angles_col=None, grf_col=None):
    """
    Calculates event times from motion (.mot) file based on joint angles and ground reaction forces.
    
    Args:
        mot_file_path (str): Path to the .mot file.
        joint_angles_col (str): Column name for joint angles to analyze.
        grf_col (str): Column name for ground reaction force (typically vertical GRF).
    
    Returns:
        List of tuples: (event_label, event_time)
    """
    
    if mot_file_path is None:
        mot_file_path = input("Please provide the path to the .mot file: ")


    

    events = []
    data = {}
    header_lines = 0
    
    with open(mot_file_path, 'r') as f:
        lines = f.readlines()
        for i, line in enumerate(lines):
            if line.startswith('time'):
                header_lines = i
                break
        
        columns = lines[header_lines].split()
        data_rows = [list(map(float, line.split())) for line in lines[header_lines + 1:] if line.strip()]
        
        for col in columns:
            data[col] = np.array([row[columns.index(col)] for row in data_rows])
    
    time = data.get('time', np.arange(len(data_rows)))
    
    # Detect foot contact events from GRF threshold
    if grf_col and grf_col in data:
        grf = data[grf_col]
        threshold = np.max(grf) * 0.05
        contact_frames = np.where(grf > threshold)[0]
        if len(contact_frames) > 0:
            events.append(('Foot Contact', time[contact_frames[0]]))
            events.append(('Foot Off', time[contact_frames[-1]]))
    
    return events

if __name__ == "__main__":
    pass

    