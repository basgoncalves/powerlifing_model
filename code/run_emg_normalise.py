import os
import utils
import pandas as pd
import xml.etree.ElementTree as ET
import settings

def main(target_emg_path=None, normalise_emg_list=None):
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
    savePath = os.path.abspath(target_emg_path.replace(ext, f'_normalised{ext}'))   
    utils.write_sto_file(dataFrame=target_emg_norm, 
                         file_path=savePath)

    utils.print_to_log(f"Normalised EMG data saved to: {savePath}")

if __name__ == "__main__":
    
    emg_normalise_list = []
    
    trial = utils.Trial(subject_name='Athlete_03',
                        session_name='22_07_06',
                        trial_name='sq_85')   
    
    for trialName in os.listdir(trial.parentdir):
        emgPath = os.path.join(trial.parentdir, trialName, settings.Inputs().EMG_FILTERED)
        if os.path.exists(emgPath):
            emg_normalise_list.append(emgPath)
    
    main(target_emg_path= str(trial.inputFiles.EMG_FILTERED),
            normalise_emg_list=emg_normalise_list)

    