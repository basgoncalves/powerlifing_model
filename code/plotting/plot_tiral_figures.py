import os
import paths 
import utils
import opensim as osim

def plot_from_settings():
    pass


if __name__ == "__main__":
    
    basedir = paths.SIMULATION_DIR
    subject = 'Athlete_03'  # Replace with actual subject name
    session = '22_07_06'  # Replace with actual session name
    trial_name = 'sq_70'  # Replace with actual trial name
    
    trial = paths.Trial(subject_name=subject, session_name=session, trial_name=trial_name)
    
    outputs = trial.outputFiles
    settings = paths.Settings() 
    for output_name, output_file in outputs.items():
        print(f"{output_name}: {output_file.abspath()}")
        
        if output_file.abspath().endswith('.sto'):
            data = utils.load_any_data_file(output_file.abspath())
            print(f"Data loaded for {output_name}: {data.shape}")

        elif os.isdir(output_file.abspath()):
            for root, dirs, files in os.walk(output_file.abspath()):
                for file in files:
                    if file.endswith('.sto'):
                        data = utils.load_any_data_file(os.path.join(root, file))
                        print(f"Data loaded for {file}: {data.shape}")