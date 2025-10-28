import os
import opensim as osim
import time

import xml.etree.ElementTree as ET
from xml.dom import minidom

import utils
import settings
import ceinms

def main(calibration_setup=None, osimModel_path=None, update_setupFiles=True):
    
    print('Running CEINMS calibration...')
    print(f'OpenSim version: {osim.__version__}')
    
    time.sleep(1)
    
    if not os.path.exists(calibration_setup):
        raise FileNotFoundError(f"CEINMS calibration setup file not found at {calibration_setup}")

    # change working directory to the session directory
    os.chdir(os.path.dirname(calibration_setup))


    # read <subjectFile> from calibration setup XML
    calibration_root = ET.parse(calibration_setup).getroot()
    subject_file_elem = calibration_root.find('subjectFile')
    
    # if empty, raise error that tag was not found
    if subject_file_elem is None:
        raise ValueError(f"<subjectFile> tag not found in {calibration_setup}")
    
    uncalibratedSubject_path = subject_file_elem.text.strip()
    
    # ceinms.create_ceinms_model(osimModelPath=osimModel_path, 
    #                            outputCEINMSModelPath=uncalibratedSubject_path)

    ceinms.create_calibrationCfg(osimModelPath=osimModel_path, 
                                 inputPaths=[settings.trial],
                                 outputPath=settings.Outputs().CEINMS_UNCALIBRATED_MODEL)

    ceinms.calibrate(setupXML_path=calibration_setup)
    

if __name__ == "__main__":
    
    start_time = time.time()

    # Ask user inputs
    calibration_setup = input("Enter full path to CEINMS calibration setup XML file: ").strip('"')
    osimModel_path = input("Enter full path to OpenSim model file (.osim): ").strip('"')

    utils.print_to_log(f'Running CEINMS calibration on {calibration_setup}')
    
    main(calibration_setup=calibration_setup, osimModel_path=osimModel_path)
        

    
    print(f"Execution time: {time.time() - start_time:.2f} seconds")