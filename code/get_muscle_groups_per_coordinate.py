import opensim as osim
import numpy as np
import paths
import os
import utils
import time

start_time = time.time()

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
model_path = r"C:\Git\1_current_projects\powerlifing_model\simulations\Katya_01\session1\P01_pers.osim"
calibration_cfg_file = r"C:\Git\1_current_projects\powerlifing_model\simulations\Katya_01\session1\calibrationCfg_ceinms-nn_hybrid.xml"

number_of_values = 2 # values for the mom arm check 

dofs = paths.Settings().DOFs

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
    
    # Sample points in the range
    values = np.linspace(range_min, range_max, number_of_values)
    
    relevant_muscles = []
    for muscle_name in muscles:
        muscle = model.getMuscles().get(muscle_name)
        # breakpoint()
        nonzero_found = False
        for value in values:
            coord.setValue(state, value)
            model.realizePosition(state)
            moment_arm = muscle.computeMomentArm(state, coord)
            if abs(moment_arm) > 1e-6:
                nonzero_found = True
                break
        if nonzero_found:
            relevant_muscles.append(muscle_name)
    coord_muscle_groups[coord_name] = relevant_muscles
            

# Save results to csv file each columns being a coordinate and rows being muscle groups
save_dir = os.path.dirname(model_path)
save_path = os.path.join(save_dir, "muscle_groups_by_coordinate.csv")
with open(save_path, 'w') as f:
    f.write("coordinate," + ",".join(muscles) + "\n")
    for coord, muscle_list in coord_muscle_groups.items():
        row = [coord] + ["1" if muscle in muscle_list else "0" for muscle in muscles]
        f.write(",".join(row) + "\n")

# load calibration cfg file
calibration_cfg = utils.read_xml(calibration_cfg_file)
muscleGroups = calibration_cfg.find("calibrationTargets/parametersToCalibrate/muscleGroups")

# clear existing muscle groups
if muscleGroups is not None:
    muscleGroups.clear()

# Print the results
print("Muscle groups per coordinate:")
save_path = os.path.join(save_dir, "muscle_groups_by_coordinate.txt")
with open(save_path, 'w') as f:
    f.write("Muscle groups per coordinate:\n")
    f.write("Coordinate: Muscle Groups\n")
    for coord, muscle_list in coord_muscle_groups.items():
        f.write(f"{coord}: {' '.join(muscle_list)}\n")
        print(f"{coord}: {', '.join(muscle_list)}")
        
        if not muscle_list: continue

        if coord not in  dofs: continue
        
        # add tag for each muscle group
        muscle_group_tag = utils.ET.Element("muscles")
        muscle_group_tag.text = " ".join(muscle_list)
        muscleGroups.append(muscle_group_tag)
        
# Save the updated calibration cfg file
new_filename = calibration_cfg_file.replace(".xml", "_updated.xml")
utils.save_pretty_xml(calibration_cfg, new_filename)
print(f"Updated calibration cfg file saved to {new_filename}")

# Print the path to the saved file
print(f"Results saved to {save_path}")

time_elapsed = time.time() - start_time
print(f"Time elapsed: {time_elapsed:.2f} seconds")

