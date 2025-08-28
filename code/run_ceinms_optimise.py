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
    command = [ceinms_exe, "-S", optimise_setup]
    print(f" \n Running command: {' '.join(command)} \n \n")
    breakpoint()
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in result.stdout.splitlines():
            print(line)
    except Exception as e:
        utils.print_to_log(f"Error running CEINMS optimise: {e}")
        
        
    if result.returncode != 0:
        print("Error running CEINMS optimise.")
        print(result.stdout)
        print(result.stderr)
        utils.print_to_log(f'Error running CEINMS optimise: {result.stdout}')
        raise RuntimeError(f"CEINMS optimise failed with exit code {result.returncode}")
    else:
        print("CEINMS optimise completed successfully.")
    
if __name__ == "__main__":
    
    start_time = time.time()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    ceinms_exe = os.path.join(current_dir, 'CEINMSoptimise.exe')
    ceinms_setup = os.path.dirname(current_dir) + '\\simulations\\Running_009\\session1\\runA1\\setup_optimise_ceinms.xml'

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
