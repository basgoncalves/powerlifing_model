import os
import sys
import opensim as osim
import xml.etree.ElementTree as ET
import xml.dom.minidom
from thefuzz import process # if not installed, run: pip install thefuzz
import utils
import paths


def save_pretty_xml(element, file_path):
    """Save an XML element to a file with pretty formatting."""
    tree = ET.ElementTree(element)
    with open(file_path, 'wb') as f:
        tree.write(f, encoding='utf-8', xml_declaration=True)
    # Pretty print the XML
    
    dom = xml.dom.minidom.parse(file_path)
    pretty_xml_as_string = dom.toprettyxml(indent="  ")
    with open(file_path, 'w') as f:
        f.write(pretty_xml_as_string)
        
def best_match(list1, list2):
    """
    Find the best match for each item in list1 from list2 using fuzzy matching.
    
    Args:
        list1 (list): List of items to match.
        list2 (list): List of items to match against.
        
    Returns:
        dict: A dictionary with items from list1 as keys and their best matches from list2 as values.
    """
    matches = {}
    for item in list1:
        match_score = 0
        for item2 in list2:
            # Simple manual string similarity: ratio of matching characters to max length
            matches_count = sum(1 for a, b in zip(item.lower(), item2.lower()) if a == b)
            match_score = matches_count / max(len(item), len(item2))
            if match_score > 0.3:
                matches[item] = item2
                break
            else:
                matches[item] = None
    return matches

def create_excitation_mapping(osim_model_path, emg_path, save_path):
    """
    Create an excitation mapping from OpenSim model muscles to EMG data.
    
    Args:
        osim_model (osim.Model): The OpenSim model.
        emg_path (str): Path to the EMG data file.
        
    Returns:
        dict: A dictionary mapping muscle names to EMG labels.
    """
    osim_model = osim.Model(osim_model_path)
    muscles = osim_model.getMuscles()
    muscle_list = [muscle.getName() for muscle in muscles]
    
    emg_data = utils.load_any_data_file(emg_path)
    emg_labels = emg_data.columns.tolist()
    
    if 'time' in emg_labels:
        emg_labels.remove('time')
    
    muscle_dict = {muscle: muscle for muscle in muscle_list}

    # Create root element
    tree = ET.ElementTree()
    root = ET.Element('excitationGenerator')

    # Add inputSignals element
    input_signals = ET.SubElement(root, 'inputSignals', {'type': 'EMG'})
    input_signals.text = ' '.join(emg_labels)

    # Add mapping element
    mapping = ET.SubElement(root, 'mapping')

    best_matches = best_match(muscle_list, emg_labels)
    for muscle in muscle_list:
        muscle_dict[muscle] = best_matches.get(muscle, None)
        if muscle_dict[muscle] is None:
            excitation = ET.SubElement(mapping, 'excitation', {'id': muscle})
        else:
            excitation = ET.SubElement(mapping, 'excitation', {'id': muscle})
            input_elem = ET.SubElement(excitation, 'input', {'weight': '1'})
            input_elem.text = muscle_dict[muscle]  # Use the best match from EMG labels

    # Write to XML file
    tree = ET.ElementTree(root)
    save_pretty_xml(root, save_path)
    print(f"XML saved to {save_path}")

    return muscle_dict, emg_labels


if __name__ == "__main__":
    import time
    current_dir = os.path.dirname(os.path.abspath(__file__))
    CEINMS_NN_DIR = os.path.dirname(current_dir)

    print("\033[93mWARNING: Please check if the path is correct. If not change \033[0m")
    print(f"CEINMS NN directory: {CEINMS_NN_DIR}")
    osim_version = osim.__version__
    print(f"OpenSim version: {osim_version}")
    time.sleep(1)
    
    # Example usage
    subject_name = 'Katya_01'
    session_name = 'session1'
    trial_name = 'files_in_run01'

    analysis = paths.Analysis()
    
    
    trial = paths.Trial(subject_name=subject_name, session_name=session_name, trial_name=trial_name)
    
    osim_model_path = trial.path + '\\' + 'P01_pers.osim'
    emg_path = trial.path + '\\' + 'filtered_emg.mot'
    save_path = trial.path + '\\' + 'excitationGenerator.xml'
    create_excitation_mapping(osim_model_path, emg_path, save_path)