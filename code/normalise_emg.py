import os
import paths
import utils
import pandas as pd

def main(target_emg_path: str, normalise_emg_list: list, save_path: str = None):
    """
    Normalises EMG data based on a target EMG file.
    The target EMG file is used to scale the other EMG files in the list.
    """
    
    target_emg = utils.load_any_data_file(target_emg_path)
    max_values = pd.DataFrame(columns=target_emg.columns)
    # Calculate the max of each EMG channel in normalise_emg_list
    for emg_file in normalise_emg_list:
        if not os.path.exists(emg_file):
            utils.print_to_log(f"EMG file not found: {emg_file}")
            continue
        emg_data = utils.load_any_data_file(emg_file)
        if emg_data is not None:
            max_values = pd.concat([max_values, pd.DataFrame([emg_data.max()])], ignore_index=True)
        else:
            print(f"Warning: Could not load EMG data from {emg_file}")
            
    if max_values.empty:
        utils.print_to_log("No valid EMG data found in the provided list.")
    
    
    if target_emg is None:
        utils.print_to_log(f"Target EMG file not found or could not be loaded: {target_emg_path}")
    
    
    # Normalise the target EMG to its own max values
    max_per_column = max_values.max(axis=0)
    target_emg_norm = target_emg.divide(max_per_column, axis=1)
    
    # Save the normalised target EMG
    ext = os.path.splitext(target_emg_path)[1]
    target_emg_norm.to_csv(target_emg_path.replace(ext, f'_normalised{ext}'), index=False)
    
    utils.print_to_log(f"Normalised EMG data saved to: {target_emg_path.replace(ext, f'_normalised{ext}')}")
    
if __name__ == "__main__":
    
    emg_normalise_list = []
    for trial_name in paths.Settings().TRIAL_TO_ANALYSE:
        trial = paths.Trial(subject_name=paths.Analysis().SUBJECTS[0].name,
                            session_name=paths.Analysis().SUBJECTS[0].SESSIONS[0].name,
                            trial_name=trial_name)
        
        filepath = trial.inputFiles['EMG_MOT'].output
        if os.path.exists(filepath):
            emg_normalise_list.append(filepath)
        else:
            print(f"EMG file not found: {filepath}")
    
          
    main(target_emg_path= paths.Analysis().SUBJECTS[0].SESSIONS[0].TRIALS[0].inputFiles['EMG_MOT'].abspath(),
                normalise_emg_list=emg_normalise_list)
    
    
    
    