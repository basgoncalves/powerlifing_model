import os
import opensim as osim
import paths
import utils
import numpy as np

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MUSCLE_COORDINATES_CSV = os.path.join(CURRENT_DIR, "muscle_groups_by_coordinates.csv")

def muscle_groups_per_coordinate_to_csv(model_path):
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
        values = np.linspace(range_min, range_max, 3)
        for muscle_name in muscles:
            muscle = model.getMuscles().get(muscle_name)
            nonzero_found = False
            for value in values:
                coord.setValue(state, value)
                model.realizeVelocity(state)
                moment_arm = muscle.computeMomentArm(state, coord)
                if abs(moment_arm) > 1e-3:
                    nonzero_found = True
                    break
            if nonzero_found:
                coord_muscle_groups[coord_name].append(muscle_name)

    # Save results to csv file each columns being a coordinate and rows being muscle groups
    with open(MUSCLE_COORDINATES_CSV, 'w') as f:
        f.write("coordinate," + ",".join(muscles) + "\n")
        for coord, muscle_list in coord_muscle_groups.items():
            row = [coord] + ["1" if muscle in muscle_list else "0" for muscle in muscles]
            f.write(",".join(row) + "\n")
    
    print(f"Muscle groups by coordinate saved to {MUSCLE_COORDINATES_CSV}")

    
if __name__ == "__main__":
    
    model_path = paths.USED_MODEL
    # ceinms_unCalibratedModel = paths.CEINMS_UNCALIBRATED_MODEL
    ceinms_unCalibratedModel_path = input("Enter the path to the CEINMS uncalibrated model file: ")
    
    if not os.path.exists(ceinms_unCalibratedModel_path):
        raise FileNotFoundError(f"CEINMS uncalibrated model file not found: {ceinms_unCalibratedModel_path}")
    
    uncalibratedModel_ceinms = utils.read_xml(ceinms_unCalibratedModel_path)

    # if MUSCLE_COORDINATES_CSV does not exist, create it
    if not os.path.exists(MUSCLE_COORDINATES_CSV):
        muscle_groups_per_coordinate_to_csv(model_path)
    
    # load the muscle groups from the csv file
    muscleGroups = utils.pd.read_csv(MUSCLE_COORDINATES_CSV, index_col=0)

    # Create a new dofSet in the uncalibrated model
    dofSet = uncalibratedModel_ceinms.find('dofSet')
    [dofSet.remove(dof) for dof in dofSet.findall('dof')] # clear dofSet

    # loop for each row (coordinate)
    for coordinate, muscleList in muscleGroups.iterrows():
        if coordinate not in paths.DOFs:
            print(f"Skipping coordinate '{coordinate}' as it is not in the defined DOFs.")
            continue
        
        # create a new dof element
        dof = utils.ET.Element('dof')
        
        # add elemenet "name"
        dofName = utils.ET.SubElement(dof, 'name')
        dofName.text = coordinate
        
        # add element "mtuNameSet"
        mtuNameSet = utils.ET.SubElement(dof, 'mtuNameSet')
        
        # add muscle groups to the mtuNameSet
        usedMuscles =[muscle for muscle, value in muscleList.items() if value == 1] 
        mtuNameSet.text = ' '.join(usedMuscles)            
        
        # append the dof to the dofSet
        dofSet.append(dof)

    # add the opensimModelFile path
    modelFile = uncalibratedModel_ceinms.find('opensimModelFile')
    modelFile.text = os.path.relpath(model_path, start=os.path.dirname(ceinms_unCalibratedModel_path))

    # save the modified uncalibrated model
    utils.save_pretty_xml(uncalibratedModel_ceinms, ceinms_unCalibratedModel_path)

    print(f"Uncalibrated model with muscle groups saved to {ceinms_unCalibratedModel_path}")