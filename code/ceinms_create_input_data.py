import xml.etree.ElementTree as ET
from xml.dom import minidom
import os

def create_input_data_xml(setup_xml):
    """
    Generates an XML file for CEINMS input data.

    Args:
        dofs (list): A list of degree of freedom names.
        output_filepath (str): The path to save the generated XML file.
        muscle_analysis_path (str): Path to the muscle analysis results folder.
        excitations_file (str): Path to the excitations file.
        external_torques_file (str): Path to the external torques file.
        motion_file (str): Path to the motion file.
        external_loads_file (str): Path to the external loads file.
        start_stop_time (str): A string with start and stop times separated by a space.
    """

    setup = ET.parse(setup_xml).getroot()
    trial_path = setup.find('trial').text
    muscle_analysis_path = setup.find('outputs/ma').text
    excitations_file = setup.find('emg_mot').text
    external_torques_file = setup.find('externalTorquesFile').text
    # Create the root element
    root = ET.Element('inputData')

    # Add child elements with their respective text content
    ET.SubElement(root, 'muscleTendonLengthFile').text = f'{muscle_analysis_path}/_MuscleAnalysis_Length.sto'
    ET.SubElement(root, 'excitationsFile').text = excitations_file
    
    # Create the momentArmsFiles parent element
    moment_arms_files = ET.SubElement(root, 'momentArmsFiles')
    
    # Add a momentArmsFile for each degree of freedom
    for dof in dofs:
        moment_arm_file = ET.SubElement(moment_arms_files, 'momentArmsFile')
        moment_arm_file.set('dofName', dof)
        moment_arm_file.text = f'{muscle_analysis_path}/_MuscleAnalysis_MomentArm_{dof}.sto'

    ET.SubElement(root, 'externalTorquesFile').text = external_torques_file
    ET.SubElement(root, 'motionFile').text = motion_file
    ET.SubElement(root, 'externalLoadsFile').text = external_loads_file
    ET.SubElement(root, 'startStopTime').text = start_stop_time

    # Create a new XML file with the generated tree
    xml_str = ET.tostring(root, 'utf-8')
    
    # Use minidom for pretty printing
    reparsed = minidom.parseString(xml_str)
    pretty_xml_str = reparsed.toprettyxml(indent="   ", newl="\n")

    # Write to file, skipping the xml declaration line added by minidom
    with open(output_filepath, "w") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n')
        f.write(pretty_xml_str.split("\n",1)[1])

if __name__ == "__main__":
    # This list should be dynamically obtained from the OpenSim model
    # For this example, we use the list from the original XML.
    all_dofs = [
        "ankle_angle_l"
    ]
    
    output_dir = os.path.dirname(os.path.abspath(__file__))
    output_file = os.path.join(output_dir, 'inputData.xml')
    
    # Generate the XML file
    create_input_data_xml(all_dofs, output_file)
    
    print(f"Successfully created '{output_file}'")

