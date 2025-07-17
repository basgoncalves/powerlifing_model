import os
import opensim as osim
import paths
import utils
import time
import subprocess
import xml.etree.ElementTree as ET
import paths
import msk_modelling_python 
print(osim.__version__)

def main(calibration_setup=None):
    
    print('Running CEINMS calibration...')
    # Prepare CEINMS calibration executable and setup file paths
    ceinms_calibration_exe = paths.CEINMS_CALIBRATION_EXE

    if not os.path.exists(ceinms_calibration_exe):
        raise FileNotFoundError(f"CEINMS calibration executable not found at {ceinms_calibration_exe}")

    if not os.path.exists(calibration_setup):
        raise FileNotFoundError(f"CEINMS calibration setup file not found at {calibration_setup}")

    # change working directory to the session directory
    os.chdir(os.path.dirname(calibration_setup))

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
    command = [ceinms_calibration_exe, "-S", calibration_setup]
    print(f"Running command: {' '.join(command)}")
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in result.stdout.splitlines():
            print(line)
    except Exception as e:
        print(f"Error running CEINMS calibration: {e}")
        exit()
        
    if result.returncode != 0:
        print("Error running CEINMS calibration.")
        print(result.stdout)
        print(result.stderr)
        utils.print_to_log(f'Error running CEINMS calibration: {result.stdout}')
        raise RuntimeError(f"CEINMS calibration failed with exit code {result.returncode}")
    else:
        print("CEINMS calibration completed successfully.")
    
if __name__ == "__main__":
    
    start_time = time.time()
     
    # Run CEINMS calibration
    try:
        utils.print_to_log(f'Running CEINMS calibration on {paths.SUBJECT} / {paths.TRIAL_NAME}')
        main(paths.CEINMS_SETUP_CALIBRATION)    
    except Exception as e:
        print(f"Error during CEINMS calibration: {e}")
        utils.print_to_log(f'{time.time()}: Error during CEINMS calibration: {e}')
        exit(1)
    
    print("CEINMS calibration completed successfully.")
    message = f"Execution time: {time.time() - start_time:.2f} seconds"
    utils.print_to_log(f'CEINMS calibration completed successfully. {message}')
