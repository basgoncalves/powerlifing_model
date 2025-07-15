import c3d

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

if __name__ == "__main__":
    import paths
    c3d_file_path = paths.C3D_PATH  # Adjust this path as needed
    events = get_events_from_c3d(c3d_file_path)
    for event in events:
        print(f"Event: {event[0]}, Time: {event[1]:.2f} seconds")