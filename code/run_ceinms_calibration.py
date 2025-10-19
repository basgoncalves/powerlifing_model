import os
import opensim as osim
from sklearn import tree
import paths
import utils
import time
import subprocess
import xml.etree.ElementTree as ET
import paths
import xml.etree.ElementTree as ET
from xml.dom import minidom

def create_ceinms_subject_file(osimModel_path, subject_id, output_path):
    """
    Create a CEINMS subject XML file with muscle-tendon unit parameters and DOF mappings.
    
    Args:
        osim_model_path: Path to the OpenSim model file
        subject_data: Dictionary containing subject-specific parameters
        output_path: Path where the subject XML file will be saved
    """
    
    osimModel = osim.Model(osimModel_path)
    state = osimModel.initSystem()  
    
    # Create root element
    root = ET.Element("subject")
    
    # Add mtuDefault section with curves and default parameters
    mtu_default = ET.SubElement(root, "mtuDefault")
    
    # EMG delay
    em_delay = ET.SubElement(mtu_default, "emDelay")
    em_delay.text = "0.015"
    
    # Percentage change
    percentage_change = ET.SubElement(mtu_default, "percentageChange")
    percentage_change.text = "0.15"
    
    # Damping
    damping = ET.SubElement(mtu_default, "damping")
    damping.text = "0.1"
    
    # Add curves (activeForceLength, passiveForceLength, forceVelocity, tendonForceStrain)
    curves_data = {
        "activeForceLength": {
            "xPoints": "-5 0 0.401 0.402 0.4035 0.52725 0.62875 0.71875 0.86125 1.045 1.2175 1.4387 1.6187 1.62 1.621 2.2 5",
            "yPoints": "0 0 0 0 0 0.22667 0.63667 0.85667 0.95 0.99333 0.77 0.24667 0 0 0 0 0"
        },
        "passiveForceLength": {
            "xPoints": "-5 0.998 0.999 1 1.1 1.2 1.3 1.4 1.5 1.6 1.601 1.602 5",
            "yPoints": "0 0 0 0 0.035 0.12 0.26 0.55 1.17 2 2 2 2"
        },
        "forceVelocity": {
            "xPoints": "-10 -1 -0.6 -0.3 -0.1 0 0.1 0.3 0.6 0.8 10",
            "yPoints": "0 0 0.08 0.2 0.55 1 1.4 1.6 1.7 1.75 1.75"
        },
        "tendonForceStrain": {
            "xPoints": " ".join([str(i * 0.001) for i in range(101)]),  # 0 to 0.1 by 0.001
            "yPoints": "0 0.0012652 0.0073169 0.016319 0.026613 0.037604 0.049078 0.060973 0.073315 0.086183 0.099678 0.11386 0.12864 0.14386 0.15928 0.17477 0.19041 0.20658 0.22365 0.24179 0.26094 0.28089 0.30148 0.32254 0.34399 0.36576 0.38783 0.41019 0.43287 0.45591 0.4794 0.50344 0.52818 0.55376 0.58022 0.60747 0.63525 0.66327 0.69133 0.71939 0.74745 0.77551 0.80357 0.83163 0.85969 0.88776 0.91582 0.94388 0.97194 1 1.0281 1.0561 1.0842 1.1122 1.1403 1.1684 1.1964 1.2245 1.2526 1.2806 1.3087 1.3367 1.3648 1.3929 1.4209 1.449 1.477 1.5051 1.5332 1.5612 1.5893 1.6173 1.6454 1.6735 1.7015 1.7296 1.7577 1.7857 1.8138 1.8418 1.8699 1.898 1.926 1.9541 1.9821 2.0102 2.0383 2.0663 2.0944 2.1224 2.1505 2.1786 2.2066 2.2347 2.2628 2.2908 2.3189 2.3469 2.375 2.4031 2.4311"
        }
    }
    
    for curve_name, curve_data in curves_data.items():
        curve = ET.SubElement(mtu_default, "curve")
        name = ET.SubElement(curve, "name")
        name.text = curve_name
        x_points = ET.SubElement(curve, "xPoints")
        x_points.text = curve_data["xPoints"]
        y_points = ET.SubElement(curve, "yPoints")
        y_points.text = curve_data["yPoints"]
       
    
    # Add MTU parameters from osimModel (you'll need to populate this with actual muscle data)
    mtu_set = ET.SubElement(root, "mtuSet")
    muscles = osimModel.getMuscles()
    for muscle in muscles:
        mtu = ET.SubElement(mtu_set, "mtu")
        name = ET.SubElement(mtu, "name")
        name.text = muscle.getName()
        
        c1 = ET.SubElement(mtu, "c1")
        c1.text = '-0.5'
        
        c2 = ET.SubElement(mtu, "c2")
        c2.text = '-0.5'
                
        optimalFibreLength = ET.SubElement(mtu, "optimalFibreLength")
        optimalFibreLength.text = str(muscle.get_optimal_fiber_length())
        
        pennationAngle = ET.SubElement(mtu, "pennationAngle")
        pennationAngle.text = str(muscle.get_pennation_angle_at_optimal())
        
        tendonSlackLength = ET.SubElement(mtu, "tendonSlackLength")
        tendonSlackLength.text = str(muscle.get_tendon_slack_length())

        maxIsometricForce = ET.SubElement(mtu, "maxIsometricForce")
        maxIsometricForce.text = str(muscle.get_max_isometric_force())

        strengthCoefficient = ET.SubElement(mtu, "strengthCoefficient")
        strengthCoefficient.text = str(1)

    # Add dofSet section
    dof_set = ET.SubElement(root, "dofSet")
    
    dofSet_osim = osimModel.getCoordinateSet()
    n_dofs = dofSet_osim.getSize()
    dof_mappings = {}
    for i in range(n_dofs):
        
        dof_name = dofSet_osim.get(i).getName()
        
        # Find muscles that span this DOF
        spanning_muscles, spanning_muscles_index = utils.muscles_per_coordinate(osimModel, dof_name)
        muscle_names = " ".join(spanning_muscles)
        dof_mappings[dof_name] = muscle_names
        
        if len(spanning_muscles) == 0:
            print(f"Warning: No muscles found spanning DOF '{dof_name}'")
            continue
        
        # Add to dofSet
        dof = ET.SubElement(dof_set, "dof")
        name = ET.SubElement(dof, "name")
        name.text = dof_name
        mtu_name_set = ET.SubElement(dof, "mtuNameSet")
        mtu_name_set.text = muscle_names
        print(f"Mapped DOF '{dof_name}' to muscles: {muscle_names}")
        
    time.sleep(1)
    
    # Add calibration info
    calibration_info = ET.SubElement(root, "calibrationInfo")
    uncalibrated = ET.SubElement(calibration_info, "uncalibrated")
    
    subjectID = ET.SubElement(uncalibrated, "subjectID")
    subjectID.text = subject_id
    
    additional_info = ET.SubElement(uncalibrated, "additionalInfo")
    additional_info.text = "TendonSlackLength and OptimalFibreLength scaled with Winby-Modenese"
    
    # Add OpenSim model file reference
    opensim_model_file = ET.SubElement(root, "opensimModelFile")
    opensim_model_file.text = osimModel_path
    
    tree = ET.ElementTree(root)
    utils.save_pretty_xml(tree, output_path)
    print(f"CEINMS subject file created: {output_path}")
    
    time.sleep(2)

def main(calibration_setup=None, osimModel_path=None, update_setupFiles=True):
    
    print('Running CEINMS calibration...')
    print(f'OpenSim version: {osim.__version__}')
    
    time.sleep(1)
    
    # Prepare CEINMS calibration executable and setup file paths
    ceinms_calibration_exe = paths.CEINMS_CALIBRATION_EXE

    if not os.path.exists(ceinms_calibration_exe):
        raise FileNotFoundError(f"CEINMS calibration executable not found at {ceinms_calibration_exe}")

    if not os.path.exists(calibration_setup):
        raise FileNotFoundError(f"CEINMS calibration setup file not found at {calibration_setup}")

    # change working directory to the session directory
    os.chdir(os.path.dirname(calibration_setup))

    # create uncalibrated subject file if it does not exist
    subject_id = osimModel_path.split(os.sep)[-1].replace('.osim', '')

    # read <subjectFile> from calibration setup XML
    root = ET.parse(calibration_setup).getroot()
    subject_file_elem = root.find('subjectFile')
    
    # if empty, raise error that tag was not found
    if subject_file_elem is None:
        raise ValueError(f"<subjectFile> tag not found in {calibration_setup}")
    
    uncalibratedSubject_path = subject_file_elem.text.strip()
    
    create_ceinms_subject_file(osimModel_path=osimModel_path, 
                               subject_id=subject_id, 
                               output_path=uncalibratedSubject_path)

    # Parse the outputDirectory from the calibration setup XML
    tree = ET.parse(calibration_setup)
    root = tree.getroot()
    output_dir = None
    for elem in root.iter():
        if elem.tag == "outputDirectory":
            output_dir = elem.text
            break

    if output_dir:
        print(f"Found output directory: {output_dir}")
        if not os.path.exists(output_dir):
            print("Output directory does not exist. Creating it...")
            os.makedirs(output_dir)
    else:
        print(f"Warning: Could not find <outputDirectory> tag in {calibration_setup}.")

    # Run the CEINMS calibration executable
    command = f"{str(ceinms_calibration_exe)} -S {str(calibration_setup)}"
    
    log_file_path = os.path.join(os.path.abspath(output_dir), 'calibration.log')

    cmd_with_redirect = f"{command} 2>&1 | Tee-Object -FilePath '{log_file_path}'; exit"
    
    print(f"Running command: {command}")
    try:
        
        process = subprocess.Popen(
            ["powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", cmd_with_redirect],
            creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        process.wait()
        print(f"CEINMS calibration process finished!")
    except Exception as e:
        print(f"Error running CEINMS calibration: {e}")
        exit()

    
if __name__ == "__main__":
    
    start_time = time.time()

    # Ask user inputs
    calibration_setup = input("Enter full path to CEINMS calibration setup XML file: ").strip()
    osimModel_path = input("Enter full path to OpenSim model file (.osim): ").strip()
    
    
    # Run CEINMS calibration
    try:
        utils.print_to_log(f'Running CEINMS calibration on {calibration_setup}')
        main(calibration_setup=calibration_setup, osimModel_path=osimModel_path)
        
    except Exception as e:
        print(f"Error during CEINMS calibration: {e}")
        utils.print_to_log(f'{time.time()}: Error during CEINMS calibration: {e}')
        exit(1)
    
    
    # print success message and update log
    message = f"Execution time: {time.time() - start_time:.2f} seconds"
    utils.print_to_log(f'CEINMS calibration completed successfully. {message}')
