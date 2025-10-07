import os
import paths
import opensim as osim
import utils


def run(muscle_forces_path, osim_modelPath):
    
    muscle_forces = utils.load_any_data_file(muscle_forces_path)
    model = osim.Model(osim_modelPath)
    model_muscles = model.getMuscles()
    for muscle in muscle_forces.columns:
        try:
            muscle_obj = model_muscles.get(muscle)
        except Exception as e:
            print(f"Error retrieving muscle '{muscle}': {e}")
            continue
                
        # Normalize the muscle forces
        normalized_forces = muscle_forces[muscle] / muscle_obj.getMaxIsometricForce()
        
        # Save the normalized forces back to the DataFrame
        muscle_forces[muscle] = normalized_forces
    
    # Save the normalized muscle forces to a new file
    header = utils.load_sto_header(muscle_forces_path)
    utils.write_sto_file(muscle_forces, muscle_forces_path.replace('.sto', '_normalised.sto'), header=header)
    
    print(f"Normalized muscle forces saved to {muscle_forces_path.replace('.sto','_normalised.sto')}")

if __name__ == '__main__':
    # Define the paths for the OpenSim model and the setup file
    osim_modelPath = paths.USED_MODEL
    muscle_forces_path = paths.SO_OUTPUT + "//SO_StaticOptimization_force.sto"
    
    utils.print_to_log(f'Normalizing muscle forces for: {paths.SUBJECT} / {paths.TRIAL_NAME} / {osim_modelPath}')

    run(muscle_forces_path = muscle_forces_path, 
        osim_modelPath = osim_modelPath)
    
    utils.print_to_log(f'Normalization of muscle forces completed. Data saved to: {muscle_forces_path.replace(".sto", "_normalised.sto")}')