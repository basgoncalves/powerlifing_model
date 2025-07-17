import opensim as osim
import numpy as np
import paths
import os
import utils

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = paths.USED_MODEL

# Load the model
model = osim.Model(model_path)
state = model.initSystem()

# Get coordinates and muscles
coordinates = [coord.getName() for coord in model.getCoordinateSet()]
muscles = [muscle.getName() for muscle in model.getMuscles()]

# Prepare results dictionary
coord_muscle_groups = {coord: [] for coord in coordinates}

# For each coordinate, vary it through its range and check muscle moment arms
for coord_name in coordinates:
    print(f"Processing coordinate: {coord_name}")
    coord = model.getCoordinateSet().get(coord_name)
    
    # skip if coordinate is locked
    if coord.get_locked():
        print(f"Skipping locked coordinate: {coord_name}")
        continue
    
    # Get coordinate range
    range_min = coord.getRangeMin()
    range_max = coord.getRangeMax()
    # Sample 10 points in the range
    values = np.linspace(range_min, range_max, 10)
    for muscle_name in muscles:
        muscle = model.getMuscles().get(muscle_name)
        nonzero_found = False
        for value in values:
            coord.setValue(state, value)
            model.realizeVelocity(state)
            moment_arm = muscle.computeMomentArm(state, coord)
            if abs(moment_arm) > 1e-6:
                nonzero_found = True
                break
        if nonzero_found:
            coord_muscle_groups[coord_name].append(muscle_name)

# Save results to csv file each columns being a coordinate and rows being muscle groups
save_path = os.path.join(CURRENT_DIR, "muscle_groups_by_coordinate.csv")
with open(save_path, 'w') as f:
    f.write("coordinate," + ",".join(muscles) + "\n")
    for coord, muscle_list in coord_muscle_groups.items():
        row = [coord] + ["1" if muscle in muscle_list else "0" for muscle in muscles]
        f.write(",".join(row) + "\n")

    