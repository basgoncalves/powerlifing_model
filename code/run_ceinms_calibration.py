import os
import opensim as osim
import paths
import utils
import time
import subprocess
import xml.etree.ElementTree as ET
import paths

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
    command = f"{str(ceinms_calibration_exe)} -S {str(calibration_setup)}"
    
    log_file_path = os.path.join(os.path.abspath(output_dir), 'calibration.log')

    cmd_with_redirect = f"{command} 2>&1 | Tee-Object -FilePath '{log_file_path}'; exit"

    batFile = os.path.join(os.path.abspath(output_dir), 'run_ceinms_cal_nn_hybrid.bat')
    
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

    analysis = utils.Analysis()

    id = 0
    subjectName = analysis.SUBJECTS[id].name
    sessionName = analysis.SUBJECTS[id].SESSIONS[0].name
    trialName = analysis.SUBJECTS[id].SESSIONS[0].TRIALS[0].name

    trial = utils.Trial(subject_name=subjectName, session_name=sessionName, trial_name=trialName)

    # Run CEINMS calibration
    try:
        utils.print_to_log(f'Running CEINMS calibration on {subjectName} / {trialName}')
        main(calibration_setup=trial.inputFiles['CEINMS_CALIBRATION_SETUP'].abspath())
    except Exception as e:
        print(f"Error during CEINMS calibration: {e}")
        utils.print_to_log(f'{time.time()}: Error during CEINMS calibration: {e}')
        exit(1)
    
    print("CEINMS calibration completed successfully.")
    message = f"Execution time: {time.time() - start_time:.2f} seconds"
    utils.print_to_log(f'CEINMS calibration completed successfully. {message}')
