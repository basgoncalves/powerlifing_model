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
    
    # get header
    header = utils.load_sto_header(target_emg_path)
    
    # Save the normalised target EMG
    ext = os.path.splitext(target_emg_path)[1]
    utils.write_sto_file(data=target_emg_norm, 
                         file_path=target_emg_path.replace(ext, f'_normalised{ext}'),
                         header=header)
    
    utils.print_to_log(f"Normalised EMG data saved to: {target_emg_path.replace(ext, f'_normalised{ext}')}")
    
if __name__ == "__main__":
    
    emg_normalise_list = []
    subject = 1
    for trial_name in paths.Settings().TRIAL_TO_ANALYSE:
        trial = paths.Trial(subject_name=paths.Analysis().SUBJECTS[subject].name,
                            session_name=paths.Analysis().SUBJECTS[subject].SESSIONS[0].name,
                            trial_name=trial_name)
        
        filepath = trial.inputFiles['EMG_MOT'].abspath()
        if os.path.exists(filepath):
            emg_normalise_list.append(filepath)
        else:
            print(f"EMG file not found: {filepath}")
    
    # loop through all the trials and normalise EMG data
    for  i, trial_name in enumerate(paths.Settings().TRIAL_TO_ANALYSE):
        trial = paths.Trial(subject_name=paths.Analysis().SUBJECTS[subject].name,
                            session_name=paths.Analysis().SUBJECTS[subject].SESSIONS[0].name,
                            trial_name=trial_name)
        
        try:
            main(target_emg_path= trial.inputFiles['EMG_MOT'].abspath(),
                 normalise_emg_list=emg_normalise_list)
        except Exception as e:
            print(f"Error normalising EMG data for trial {trial.name}: {e}")
    utils.print_to_log(f"EMG data normalised for all trials in subject {paths.Analysis().SUBJECTS[subject].name}")