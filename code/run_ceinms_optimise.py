import os
import opensim as osim
import paths
import utils
import time
import subprocess
import xml.etree.ElementTree as ET
import paths

print(osim.__version__)

def main(ceinms_exe, optimise_setup=None):
    
    if not os.path.exists(ceinms_exe):
        utils.print_to_log(f'CEINMS optimise executable not found at {ceinms_exe}')
        raise FileNotFoundError(f"CEINMS optimise executable not found at {ceinms_exe}")

    if not os.path.exists(optimise_setup):
        utils.print_to_log(f'CEINMS optimise setup file not found at {optimise_setup}')
        raise FileNotFoundError(f"CEINMS optimise setup file not found at {optimise_setup}")

    # change working directory to the session directory
    os.chdir(os.path.dirname(optimise_setup))

    # Parse the outputDirectory from the calibration setup XML
    tree = ET.parse(optimise_setup)
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
        utils.print_to_log(f"Warning: Could not find <outputDirectory> tag in {optimise_setup}.")

    # Run the CEINMS optimise executable
    command = f"{str(ceinms_exe)} -S {str(optimise_setup)}"
    print(f" \n Running command: {command} \n \n")

    trial_path = os.path.dirname(optimise_setup)
    exe_dir = os.path.dirname(ceinms_exe)
    log_file_path = os.path.join(trial_path, "ceinms.log")

    cmd_with_redirect = f"{command} 2>&1 | Tee-Object -FilePath '{log_file_path}'; exit"

    try:
        process = subprocess.Popen(
            [
                "powershell",
                "-NoExit",
                "-ExecutionPolicy",
                "Bypass",
                "-Command",
                cmd_with_redirect,
            ],
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        process.wait()

        print(f"\nOptimization complete. Log saved to: {log_file_path}")

    except FileNotFoundError:
        raise RuntimeError(
            f"Could not execute {ceinms_exe}. Check if file exists and is executable."
        )
    except Exception as e:
        raise RuntimeError(f"Error running CEINMS: {e}")
    except Exception as e:
        utils.print_to_log(f"Error running CEINMS optimise: {e}")
        

   
if __name__ == "__main__":
    
    start_time = time.time()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ceinms_exe = paths.CEINMS_OPTIMISE_EXE
    
    analysis = utils.Analysis()
    
    id = 0
    subjectName = analysis.SUBJECTS[id].name
    sessionName = analysis.SUBJECTS[id].SESSIONS[0].name
    trialName = analysis.SUBJECTS[id].SESSIONS[0].TRIALS[0].name
    
    trial = utils.Trial(subject_name=subjectName, session_name=sessionName, trial_name=trialName)
    
    ceinms_setup = trial.inputFiles['CEINMS_OPTIMISE_SETUP'].abspath()

    # Run CEINMS optimise
    try:
        main(ceinms_exe=ceinms_exe,
             optimise_setup=ceinms_setup)

    except Exception as e:
        print(f"Error during CEINMS optimise: {e}")
        raise (f"CEINMS optimise failed: {e}")
    
    print("CEINMS optimise completed successfully.")
    message = f"Execution time: {time.time() - start_time:.2f} seconds"
    print(f'CEINMS optimise completed successfully. {message}')
