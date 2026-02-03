"""
Convert Static Optimization (SO) activations to EMG-like excitation format.
Creates excitation generator file with all muscles for new CEINMS run.
"""

import os
import sys
import pandas as pd
import xml.etree.ElementTree as ET
import opensim as osim

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import utils


trialPath = input("Enter trial directory path: ").strip('"')
trial = utils.Analyse(trialPath=trialPath)

so_activations_path = os.path.join(trial.path, trial.so_activations)
so_activations = utils.load_any_data_file(so_activations_path)

emg_path = os.path.join(trial.path, trial.ceinms_excitations)
emg = utils.load_any_data_file(emg_path)

excitation_generator_path = os.path.join(trial.path, trial.ceinms_excitation_generator)
excitation_generator_tree = ET.parse(excitation_generator_path)
excitation_generator_root = excitation_generator_tree.getroot()

input_signals_element = excitation_generator_root.find('.//inputSignals')

# Get list of muscles from excitation generator
muscles_in_generator = []
for muscle_element in excitation_generator_root.findall('.//excitation'):
    muscle_id = muscle_element.get('id')
    muscles_in_generator.append(muscle_id)
    
    # Check if input exists
    input_element = muscle_element.find('input')
    if input_element is not None:
        print(f"Muscle {muscle_id} has input: {input_element.text}")
    else:
        print(f"Muscle {muscle_id} has no input")
        so_input = ET.SubElement(muscle_element, 'input')
        so_input.text = muscle_id
        so_input.set('weight', '1')
        
        # append signal to inputSignals
        if input_signals_element is not None:
            current_signals = input_signals_element.text.strip().split()
            current_signals.append(muscle_id)
            input_signals_element.text = ' '.join(current_signals)
 
# Check each muscle and add SO activation if no EMG input exists
for muscle in muscles_in_generator:
    if muscle not in emg.columns and muscle in so_activations.columns:
        # Interpolate SO activation to match EMG timestamps
        so_muscle_data = so_activations[muscle].values
        so_time = so_activations.index.values
        emg_time = emg.index.values
        
        interpolated_values = pd.Series(so_muscle_data, index=so_time).reindex(emg_time, method='nearest')
        emg[muscle] = interpolated_values

# Save the updated EMG file
updated_emg_path = emg_path.replace('.sto', '_with_SO_excitations.sto')
utils.write_sto_file(emg, updated_emg_path)

print(f"Updated EMG file with SO excitations saved to: {updated_emg_path}")

# Save the updated excitation generator file
updated_excitation_generator_path = excitation_generator_path.replace('.xml', '_with_SO_excitations.xml')
utils.save_pretty_xml(excitation_generator_tree, updated_excitation_generator_path)
print(f"Updated excitation generator file saved to: {updated_excitation_generator_path}")

