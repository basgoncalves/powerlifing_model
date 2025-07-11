import os
import opensim as osim
import paths
import utils

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
txt_file_path = os.path.join(CURRENT_DIR, "muscle_groups_by_coordinate.txt")


exit()
# Load the model
model = osim.Model(paths.USED_MODEL)
state = model.initSystem()

# read the txt file if it exists
if os.path.exists(txt_file_path):
    with open(txt_file_path, 'r') as f:
        lines = f.readlines()
        
    # Parse the muscle groups by coordinate 
    muscle_groups = {}
    current_coord = None
    for line in lines:
        line = line.strip()
        if line.endswith(':'):
            current_coord = line[:-1]
            muscle_groups[current_coord] = []
        elif current_coord is not None and line:
            muscle_groups[current_coord].append(line)

    # 
    print("Muscle groups loaded from file:")
    for coord, muscles in muscle_groups.items():
        print(f"{coord}: {', '.join(muscles)}")
        
        # Add muscles group to the model
        for muscle_name in muscles:
            muscle = model.getMuscles().get(muscle_name)
            if muscle:
                muscle.setCoordinate(model.getCoordinateSet().get(current_coord))
                print(f"Added {muscle_name} to coordinate {current_coord}")
            else:
                print(f"Muscle {muscle_name} not found in the model.")
        
