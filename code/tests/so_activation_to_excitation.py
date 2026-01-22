"""
Convert Static Optimization (SO) activations to EMG-like excitation format.
Creates excitation generator file with all muscles for new CEINMS run.
"""

import os
import sys
import pandas as pd
import xml.etree.ElementTree as ET
import opensim as osim

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import utils


def convert_so_activations_to_excitations(
    so_activation_file: str,
    output_excitation_file: str
):
    """
    Convert SO activation data to excitation format compatible with CEINMS.
    
    Args:
        so_activation_file: Path to SO activation .sto file
        output_excitation_file: Path to save excitation .sto file
        
    Returns:
        pd.DataFrame: Converted excitation data
    """
    print(f"Loading SO activations from: {so_activation_file}")
    
    # Load SO activation data
    so_data = utils.load_any_data_file(so_activation_file)
    
    # SO activations are already in the correct format (0-1 range)
    # Just need to ensure proper column naming
    excitation_data = so_data.copy()
    
    # Save as excitation file
    print(f"Saving excitations to: {output_excitation_file}")
    
    # Write in OpenSim .sto format
    with open(output_excitation_file, 'w') as f:
        # Write header
        f.write(f"{os.path.basename(output_excitation_file)}\n")
        f.write(f"version=1\n")
        f.write(f"nRows={len(excitation_data)}\n")
        f.write(f"nColumns={len(excitation_data.columns)}\n")
        f.write(f"in_degrees=no\n")
        f.write(f"endheader\n")
        
        # Write data
        excitation_data.to_csv(f, sep='\t', index=False)
    
    print(f"Conversion complete! {len(excitation_data.columns)-1} muscles converted")
    
    return excitation_data


def create_excitation_generator_from_so(
    osim_model_path: str,
    so_activation_file: str,
    output_xml_path: str,
    use_all_muscles: bool = True
):
    """
    Create excitation generator XML file using all muscles from SO activations.
    
    Args:
        osim_model_path: Path to OpenSim model
        so_activation_file: Path to SO activation file
        output_xml_path: Path to save excitation generator XML
        use_all_muscles: If True, includes all muscles from model (default: True)
        
    Returns:
        Tuple of (muscle_list, excitation_labels)
    """
    print(f"Creating excitation generator from SO activations")
    print(f"Model: {osim_model_path}")
    print(f"SO activations: {so_activation_file}")
    
    # Load OpenSim model to get all muscles
    model = osim.Model(osim_model_path)
    model.initSystem()
    muscles = model.getMuscles()
    muscle_list = [muscle.getName() for muscle in muscles]
    
    # Load SO activation data to get available muscles
    so_data = utils.load_any_data_file(so_activation_file)
    available_muscles = [col for col in so_data.columns if col != 'time']
    
    print(f"Total muscles in model: {len(muscle_list)}")
    print(f"Muscles with SO activation data: {len(available_muscles)}")
    
    # Create root element
    root = ET.Element('excitationGenerator')
    
    # Add inputSignals element - use SO activation muscle names as inputs
    input_signals = ET.SubElement(root, 'inputSignals', {'type': 'SO_Activation'})
    input_signals.text = ' '.join(available_muscles)
    
    # Add mapping element
    mapping = ET.SubElement(root, 'mapping')
    
    if use_all_muscles:
        # Map all muscles in the model
        for muscle in muscle_list:
            excitation = ET.SubElement(mapping, 'excitation', {'id': muscle})
            
            # If this muscle has SO activation data, map it with weight 1.0
            if muscle in available_muscles:
                input_elem = ET.SubElement(excitation, 'input', {'weight': '1.0'})
                input_elem.text = muscle
            else:
                # Muscle not in SO data - will need to be handled by CEINMS
                # Leave empty (CEINMS will use default behavior)
                pass
    else:
        # Only map muscles that have SO activation data
        for muscle in available_muscles:
            excitation = ET.SubElement(mapping, 'excitation', {'id': muscle})
            input_elem = ET.SubElement(excitation, 'input', {'weight': '1.0'})
            input_elem.text = muscle
    
    # Write to XML file
    tree = ET.ElementTree(root)
    utils.save_pretty_xml(tree, os.path.abspath(output_xml_path))
    
    print(f"Excitation generator XML saved to: {os.path.abspath(output_xml_path)}")
    print(f"Mapped {len(available_muscles)} muscles")
    
    return muscle_list, available_muscles


def create_hybrid_excitation_generator(
    osim_model_path: str,
    so_activation_file: str,
    emg_file: str,
    output_xml_path: str,
    so_weight: float = 0.5,
    emg_weight: float = 0.5
):
    """
    Create hybrid excitation generator combining SO activations and EMG.
    
    Args:
        osim_model_path: Path to OpenSim model
        so_activation_file: Path to SO activation file
        emg_file: Path to EMG data file
        output_xml_path: Path to save excitation generator XML
        so_weight: Weight for SO activations (default: 0.5)
        emg_weight: Weight for EMG inputs (default: 0.5)
        
    Returns:
        Tuple of (muscle_list, so_muscles, emg_muscles)
    """
    print(f"Creating hybrid excitation generator")
    print(f"SO weight: {so_weight}, EMG weight: {emg_weight}")
    
    # Load OpenSim model
    model = osim.Model(osim_model_path)
    model.initSystem()
    muscles = model.getMuscles()
    muscle_list = [muscle.getName() for muscle in muscles]
    
    # Load SO activation data
    so_data = utils.load_any_data_file(so_activation_file)
    so_muscles = [col for col in so_data.columns if col != 'time']
    
    # Load EMG data
    emg_data = utils.load_any_data_file(emg_file)
    emg_labels = [col for col in emg_data.columns if col != 'time']
    
    # Get EMG to muscle mapping
    emg_mapping = utils.CEINMSParameters().EMG_muscle_mapping
    
    print(f"Total muscles in model: {len(muscle_list)}")
    print(f"SO muscles: {len(so_muscles)}")
    print(f"EMG signals: {len(emg_labels)}")
    
    # Create root element
    root = ET.Element('excitationGenerator')
    
    # Add inputSignals - combine both SO and EMG
    input_signals = ET.SubElement(root, 'inputSignals', {'type': 'Hybrid'})
    all_inputs = so_muscles + emg_labels
    input_signals.text = ' '.join(all_inputs)
    
    # Add mapping element
    mapping = ET.SubElement(root, 'mapping')
    
    for muscle in muscle_list:
        excitation = ET.SubElement(mapping, 'excitation', {'id': muscle})
        
        # Check if muscle has SO activation
        has_so = muscle in so_muscles
        
        # Check if muscle has EMG mapping
        has_emg = False
        emg_label = None
        for emg_input, mapped_muscles in emg_mapping.items():
            if muscle in mapped_muscles:
                has_emg = True
                emg_label = emg_input
                break
        
        # Add inputs based on availability
        if has_so and has_emg:
            # Hybrid: both SO and EMG available
            so_input = ET.SubElement(excitation, 'input', {'weight': str(so_weight)})
            so_input.text = muscle
            
            emg_input_elem = ET.SubElement(excitation, 'input', {'weight': str(emg_weight)})
            emg_input_elem.text = emg_label
            
        elif has_so:
            # Only SO available
            so_input = ET.SubElement(excitation, 'input', {'weight': '1.0'})
            so_input.text = muscle
            
        elif has_emg:
            # Only EMG available
            emg_input_elem = ET.SubElement(excitation, 'input', {'weight': '1.0'})
            emg_input_elem.text = emg_label
        
        # If neither available, leave empty (CEINMS will handle)
    
    # Write to XML file
    tree = ET.ElementTree(root)
    utils.save_pretty_xml(tree, os.path.abspath(output_xml_path))
    
    print(f"Hybrid excitation generator XML saved to: {os.path.abspath(output_xml_path)}")
    
    return muscle_list, so_muscles, emg_labels


if __name__ == "__main__":
    print("SO Activation to Excitation Converter")
    print("=" * 60)
    
    choice = input("Choose operation:\n1. Convert SO activations to excitations\n2. Create excitation generator from SO\n3. Create hybrid excitation generator\nEnter choice (1/2/3): ")
    
    if choice == '1':
        # Convert SO activations to excitation format
        so_file = input("Enter path to SO activation file (.sto): ").strip('"')
        output_file = input("Enter path for output excitation file (.sto): ").strip('"')
        
        convert_so_activations_to_excitations(so_file, output_file)
        
    elif choice == '2':
        # Create excitation generator from SO
        model_path = input("Enter path to OpenSim model (.osim): ").strip('"')
        so_file = input("Enter path to SO activation file (.sto): ").strip('"')
        output_xml = input("Enter path for output excitation generator XML (.xml): ").strip('"')
        
        create_excitation_generator_from_so(model_path, so_file, output_xml)
        
    elif choice == '3':
        # Create hybrid excitation generator
        model_path = input("Enter path to OpenSim model (.osim): ").strip('"')
        so_file = input("Enter path to SO activation file (.sto): ").strip('"')
        emg_file = input("Enter path to EMG file (.sto): ").strip('"')
        output_xml = input("Enter path for output hybrid excitation generator XML (.xml): ").strip('"')
        
        so_weight = float(input("Enter SO weight (0-1, default 0.5): ") or "0.5")
        emg_weight = float(input("Enter EMG weight (0-1, default 0.5): ") or "0.5")
        
        create_hybrid_excitation_generator(model_path, so_file, emg_file, output_xml, so_weight, emg_weight)
        
    else:
        print("Invalid choice")
    
    print("\nOperation complete!")
