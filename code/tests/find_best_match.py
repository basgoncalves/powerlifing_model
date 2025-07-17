import os

import matplotlib

paths = [
    r"C:\Git\1_current_projects\powerlifing_model\simulations\Athlete_03\22_07_06\sq_75",
    r"C:\Git\1_current_projects\powerlifing_model\simulations\Athlete_03\22_07_06\sq_80",
    r"C:\Git\1_current_projects\powerlifing_model\simulations\Athlete_03\22_07_06\sq_85",
    r"C:\Git\1_current_projects\powerlifing_model\simulations\Athlete_03\22_07_06\sq_90",
    r"C:\Git\1_current_projects\powerlifing_model\simulations\Athlete_03_MRI\22_07_06\sq_70",
    r"C:\Git\1_current_projects\powerlifing_model\simulations\Athlete_03_MRI\22_07_06\sq_75",
    r"C:\Git\1_current_projects\powerlifing_model\simulations\Athlete_03_MRI\22_07_06\sq_80",
    r"C:\Git\1_current_projects\powerlifing_model\simulations\Athlete_03_MRI\22_07_06\sq_85",
    r"C:\Git\1_current_projects\powerlifing_model\simulations\Athlete_03_MRI\22_07_06\sq_90"
]

def get_unique_names(paths):
    # Split each path into parts
    split_paths = [p.split(os.sep) for p in paths]

    # Transpose to compare columns
    columns = list(zip(*split_paths))

    # Find the indices where not all elements are the same
    diff_indices = [i for i, col in enumerate(columns) if len(set(col)) > 1]

    # Create unique names using the differing parts
    unique_names = []
    for parts in split_paths:
        unique = "_".join([parts[i] for i in diff_indices])
        unique_names.append(unique)
    return unique_names

def create_color_and_style_dict(labels):
    """Creates a color and style dictionary based on unique labels.
    Args:
        labels (list): List of unique labels.
        Returns:
        tuple: Two dictionaries, one for colors and one for styles.
            
    Example:
        labels = ['Athlete_03_sq_70', 'Athlete_03_sq_75', 'Athlete_03_sq_80']
        color_dict, style_dict = create_color_and_style_dict(labels)
        
    """
    
    
    color_dict = {}
    style_dict = {}
    # Extract the number (e.g., 70, 75, 80, 85, 90) from each label for color assignment
    # Assume the number is always at the end after an underscore
    numbers = [label.split('_')[-1] for label in labels]
    unique_numbers = sorted(set(numbers), key=lambda x: int(x))
    color_map = matplotlib.colormaps['tab10']
    number_to_color = {num: color_map.colors[i % 10] for i, num in enumerate(unique_numbers)}
    for label, num in zip(labels, numbers):
        color_dict[label] = number_to_color[num]
        if 'mri' in label.lower():
            style_dict[label] = '--'
        else:
            style_dict[label] = '-'
    return color_dict, style_dict

unique_names = get_unique_names(paths)
color_dict, style_dict = create_color_and_style_dict(unique_names)
for path, name in zip(paths, unique_names):
    print(f"{path} -> {name} | Color: {color_dict[name]} | Style: {style_dict[name]}")
    
    breakpoint()  # This will pause the execution for debugging