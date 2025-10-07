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
    
    trial_path = os.path.dirname(optimise_setup)
    exe_dir = os.path.dirname(ceinms_exe)
    log_file_path = os.path.join(trial_path, "ceinms.log")
    
    try:
        print("Running CEINMS optimization...")
        print(f"Executable: {ceinms_exe}")
        print(f"Setup file: {optimise_setup}")

        # PowerShell script that adds exe dir to PATH, then runs from trial dir
        ps_script = f'''
            $ErrorActionPreference = "Continue"
            $env:PATH = "{exe_dir};$env:PATH"
            Set-Location "{trial_path}"
            & "{ceinms_exe}" -S "{optimise_setup}"
            exit $LASTEXITCODE
            '''

        cmd = ["powershell", "-ExecutionPolicy", "Bypass", "-Command", ps_script]

        with open(log_file_path, "w", encoding="utf-8") as log_file:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
            )

            # Stream output
            if process.stdout:
                for line in process.stdout:
                    # print(line, end="")
                    log_file.write(line)
                    log_file.flush()

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
    ceinms_exe = os.path.join(current_dir, 'executables', 'CEINMSoptimise.exe')
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
