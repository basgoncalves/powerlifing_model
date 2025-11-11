import os
import shutil
import subprocess
import time

import numpy as np
import settings
import xml.etree.ElementTree as ET
import opensim as osim
import utils
import matplotlib.pyplot as plt
import pandas as pd
import scipy

def upWorkingDirectory():
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    os.chdir(parent_dir)
    print(f"Changed working directory to: {parent_dir}")

def importSettings():
    import settings
    settings._print()

def create_ceinms_model(osimModelPath=None, outputCEINMSModelPath=None):
    """
    Create a CEINMS subject XML file with muscle parameters extracted from the OpenSim model.
    """
    if not osimModelPath:
        osimModelPath = input("Enter path to OpenSim model (.osim): ").strip('"')

    if not outputCEINMSModelPath:
        outputCEINMSModelPath = input("Enter path to output CEINMS model (.xml): ").strip('"')

    print(f"Creating CEINMS model from OpenSim model")
    # Load the OpenSim model
    model = osim.Model(osimModelPath)
    model.initSystem()
    
    # Create the root element
    root = ET.Element("subject")
    
    # Add mtuDefault section with default curves and parameters
    mtu_default = ET.SubElement(root, "mtuDefault")
    
    # Add default parameters
    ET.SubElement(mtu_default, "emDelay").text = "0.015"
    ET.SubElement(mtu_default, "percentageChange").text = "0.15"
    ET.SubElement(mtu_default, "damping").text = "0.1"
    
    # Add default curves (using the curves from your example)
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
            "xPoints": " ".join([str(i/1000) for i in range(0, 101)]),
            "yPoints": "0 0.0012652 0.0073169 0.016319 0.026613 0.037604 0.049078 0.060973 0.073315 0.086183 0.099678 0.11386 0.12864 0.14386 0.15928 0.17477 0.19041 0.20658 0.22365 0.24179 0.26094 0.28089 0.30148 0.32254 0.34399 0.36576 0.38783 0.41019 0.43287 0.45591 0.4794 0.50344 0.52818 0.55376 0.58022 0.60747 0.63525 0.66327 0.69133 0.71939 0.74745 0.77551 0.80357 0.83163 0.85969 0.88776 0.91582 0.94388 0.97194 1 1.0281 1.0561 1.0842 1.1122 1.1403 1.1684 1.1964 1.2245 1.2526 1.2806 1.3087 1.3367 1.3648 1.3929 1.4209 1.449 1.477 1.5051 1.5332 1.5612 1.5893 1.6173 1.6454 1.6735 1.7015 1.7296 1.7577 1.7857 1.8138 1.8418 1.8699 1.898 1.926 1.9541 1.9821 2.0102 2.0383 2.0663 2.0944 2.1224 2.1505 2.1786 2.2066 2.2347 2.2628 2.2908 2.3189 2.3469 2.375 2.4031 2.4311"
        }
    }
    
    for curve_name, points in curves_data.items():
        curve = ET.SubElement(mtu_default, "curve")
        ET.SubElement(curve, "name").text = curve_name
        ET.SubElement(curve, "xPoints").text = points["xPoints"]
        ET.SubElement(curve, "yPoints").text = points["yPoints"]
    
    # Add mtuSet section
    mtu_set = ET.SubElement(root, "mtuSet")
    
    # Extract muscle parameters from OpenSim model
    muscle_set = model.getMuscles()
    for i in range(muscle_set.getSize()):
        muscle = muscle_set.get(i)
        
        # Create mtu element for each muscle
        mtu = ET.SubElement(mtu_set, "mtu")
        
        # Add muscle parameters
        ET.SubElement(mtu, "name").text = muscle.getName()
        ET.SubElement(mtu, "c1").text = "-0.5"
        ET.SubElement(mtu, "c2").text = "-0.5"
        ET.SubElement(mtu, "shapeFactor").text = "0.1"
        ET.SubElement(mtu, "optimalFibreLength").text = str(muscle.getOptimalFiberLength())
        ET.SubElement(mtu, "pennationAngle").text = str(muscle.getPennationAngleAtOptimalFiberLength())
        ET.SubElement(mtu, "tendonSlackLength").text = str(muscle.getTendonSlackLength())
        ET.SubElement(mtu, "maxIsometricForce").text = str(muscle.getMaxIsometricForce())
        ET.SubElement(mtu, "strengthCoefficient").text = "1"
    
    # Add dofSet section
    dof_set = ET.SubElement(root, "dofSet")
    
    # Define DOFs and their associated muscles
    dof_muscles = {}
    coordinates = model.getCoordinateSet()
    print('Adding muscles to DOFs...')
    for i in range(coordinates.getSize()):
        coord = coordinates.get(i)
        coord_name = coord.getName()
        
        if coord_name not in settings.DOFs:
            continue
        
        # Get muscles that cross this coordinate
        muscles_for_coord = []
        for j in range(muscle_set.getSize()):
            muscle = muscle_set.get(j)
            state = model.initSystem()
            model.realizePosition(state)
            
            try:
                moment_arm = muscle.computeMomentArm(state, coord)
                if abs(moment_arm) > 1e-6:  # Small threshold for numerical precision
                    muscles_for_coord.append(muscle.getName())
            except:
                continue
                
        if muscles_for_coord:
            dof_muscles[coord_name] = muscles_for_coord
    
    # Create DOF elements
    for dof_name, muscle_names in dof_muscles.items():
        dof = ET.SubElement(dof_set, "dof")
        ET.SubElement(dof, "name").text = dof_name
        ET.SubElement(dof, "mtuNameSet").text = " ".join(muscle_names)
    
    # Add calibrationInfo section
    calibration_info = ET.SubElement(root, "calibrationInfo")
    uncalibrated = ET.SubElement(calibration_info, "uncalibrated")
    ET.SubElement(uncalibrated, "subjectID").text = os.path.basename(osimModelPath).replace('.osim', '')
    ET.SubElement(uncalibrated, "additionalInfo").text = ''
    
    # Add opensimModelFile reference
    ET.SubElement(root, "opensimModelFile").text = os.path.relpath(osimModelPath, os.path.dirname(outputCEINMSModelPath))

    # Create the XML tree and save
    tree = ET.ElementTree(root)
    utils.save_pretty_xml(tree, outputCEINMSModelPath)

    print(f"CEINMS subject file created: {outputCEINMSModelPath}")

def create_excitation_generator(osim_model_path=None, emg_path=None, save_path=None):
    """
    Create an excitation mapping from OpenSim model muscles to EMG data.
    
    Args:
        osim_model (osim.Model): The OpenSim model.
        emg_path (str): Path to the EMG data file.
        
    Returns:
        dict: A dictionary mapping muscle names to EMG labels.
    """
    import settings
    if not osim_model_path:
        osim_model_path = input("Enter path to OpenSim model (.osim): ").strip('"')
        
    if not emg_path:
        emg_path = input("Enter path to EMG data file (.sto/.csv): ").strip('"')
        
    if not save_path:
        save_path = input("Enter path to save the excitation mapping XML file: ").strip('"')
    
    osim_model = osim.Model(osim_model_path)
    muscles = osim_model.getMuscles()
    muscleList = [muscle.getName() for muscle in muscles]
    
    emg_data = utils.load_any_data_file(emg_path)
    emg_labels = emg_data.columns.tolist()
    
    if 'time' in emg_labels:
        emg_labels.remove('time')

    # Create root element
    tree = ET.ElementTree()
    root = ET.Element('excitationGenerator')

    # Add inputSignals element
    input_signals = ET.SubElement(root, 'inputSignals', {'type': 'EMG'})
    input_signals.text = ' '.join(emg_labels)

    # Add mapping element
    mapping = ET.SubElement(root, 'mapping')
    mapping_dict = settings.EMG_muscle_mapping    
    
    for muscle in muscleList:
        used = False
        for emg_input, items in mapping_dict.items(): 
            if muscle in items: used = True; break

        if used:
            emg_label = emg_input
            excitation = ET.SubElement(mapping, 'excitation', {'id': muscle})
            input_elem = ET.SubElement(excitation, 'input', {'weight': '1'})
            input_elem.text = emg_label
        else:
            excitation = ET.SubElement(mapping, 'excitation', {'id': muscle})
    
            
    # Write to XML file
    tree = ET.ElementTree(root)
    utils.save_pretty_xml(tree, os.path.abspath(save_path))
    print(f"XML saved to {os.path.abspath(save_path)}")

    return mapping_dict, emg_labels

def create_calibrationCfg(osimModelPath=None, inputPaths: list = [], outputPath: str = None):
    """
    Create a CEINMS calibration XML configuration from input parameters.
    
    Args:
        optimiser_config: Dictionary containing optimiser settings
        tendon_type: Type of tendon model (default: "elastic")
        parameters_to_calibrate: Dictionary of parameter ranges
        objective_functions: List of objective function configurations
        muscle_groups: List of muscle groups (each group is a list of muscle names)
        trial_set_path: Path to the trial set input data
        output_path: Optional path to save the XML file
    
    Returns:
        ET.Element: Root XML element
    """
    import settings
    if not osimModelPath: 
        osimModelPath = input("Enter path to OpenSim model (.osim): ").strip('"')
    
    if not inputPaths:
        inputPaths = settings.CEINMS_CALIBRATION_TRIALS

    if not outputPath:
        outputPath = input("Enter path to save the calibration configuration XML file: ")
    
    template_cfg = os.path.join(settings.SETUP_DIR, os.path.basename(settings.Inputs().CEINMS_CALIBRATION_CFG))
    
    # read template to get structure
    tree = ET.parse(template_cfg)
    root = tree.getroot()
    
    for param in settings.CEINMSParameters().__dict__.items():
        tag, value = param
        for elem in root.findall(f'.//{tag}'):
            elem.text = str(value)

    # trialSet
    trialSet = root.find('trialSet')
    trialSet.text = ' '.join(inputPaths) 
    
    # edit muscleGroups
    muscleGroups = root.find('calibrationTargets').find('parametersToCalibrate').find('muscleGroups')
    muscleGroups.clear()
    for group, muscles in settings.Muscle_Groups.items():
        muscleGroup = ET.SubElement(muscleGroups, 'muscles')
        muscleGroup.text = ' '.join(muscles)

    # edit objectiveFunctions
    objectiveFunctions = root.find('calibrationTargets').find('objectiveFunctions')
    objectiveFunctions.clear()
    for func in settings.CEINMSParameters().Objective_Functions:
        objFunc = ET.SubElement(objectiveFunctions, 'objectiveFunction')
        for key, value in func.items():
            elem = ET.SubElement(objFunc, key)
            elem.text = str(value)
            
    targetMuscles = root.find('calibrationTargets').find('muscles')
    targetMuscles.clear()
    for muscle in settings.CEINMSParameters().Target_Muscles:
        muscleElem = ET.SubElement(targetMuscles, 'muscle')
        muscleElem.text = muscle

    tree = ET.ElementTree(root)
    utils.save_pretty_xml(tree, outputPath)
    print(f"Calibration configuration XML saved to: {os.path.abspath(outputPath)}")

    return root

def create_calibrationSetupXML(uncalibratedCEINMSModelPath=None, 
                               excitationGeneratorFile=None,
                               calibrationCfgPath=None,
                               outputSubjectFile =None, 
                               outputDirectory=None,
                               setupXMLPath=None):
    
    if not uncalibratedCEINMSModelPath:
        uncalibratedCEINMSModelPath = input("Enter path to uncalibrated CEINMS model file: ").strip('"')
    
    if not calibrationCfgPath:
        calibrationCfgPath = input("Enter path to calibration config file: ").strip('"')
    
    if not excitationGeneratorFile:
        excitationGeneratorFile = input("Enter path to excitation generator file: ").strip('"')
    
    if not outputSubjectFile:
        outputSubjectFile = uncalibratedCEINMSModelPath.replace('.xml', '_calibrated.xml')
        
    if not outputDirectory:
        outputDirectory = os.path.join(os.path.dirname(calibrationCfgPath), 'calibrationOutput')
    
    root = ET.Element("ceinmsCalibration")

    setupXMLPathDir = os.path.dirname(setupXMLPath)
    
    subjectFile = ET.SubElement(root, "subjectFile")
    subjectFile.text = os.path.relpath(uncalibratedCEINMSModelPath, setupXMLPathDir)
    
    excitationGeneratorFileTag = ET.SubElement(root, "excitationGeneratorFile")
    excitationGeneratorFileTag.text = os.path.relpath(excitationGeneratorFile, setupXMLPathDir)

    calibrationFile = ET.SubElement(root, "calibrationFile")
    calibrationFile.text = os.path.relpath(calibrationCfgPath, setupXMLPathDir)

    outputSubjectFileTag = ET.SubElement(root, "outputSubjectFile")
    outputSubjectFileTag.text = os.path.relpath(outputSubjectFile, setupXMLPathDir)

    outputDirectoryTag = ET.SubElement(root, "outputDirectory")
    outputDirectoryTag.text = os.path.relpath(outputDirectory, setupXMLPathDir)
    
    tree = ET.ElementTree(root)
    utils.save_pretty_xml(tree, setupXMLPath)

def create_input_data(MAFolder=None, excitationsFile=None, motionFile=None, 
                      externalTorquesFile=None, externalLoadsFile=None,
                      startStopTime=None):
    
    if not MAFolder:
        MAFolder = input("Enter path to Muscle Analysis folder: ").strip('"')

    if not excitationsFile:
        excitationsFile = input("Enter path to excitations file: ").strip('"')
    
    if not motionFile:
        motionFile = input("Enter path to motion file: ").strip('"')
        
    if not externalTorquesFile:
        externalTorquesFile = input("Enter path to external torques file: ").strip('"')
    
    if not externalLoadsFile:
        externalLoadsFile = input("Enter path to external loads file: ").strip('"')
        
    if not startStopTime:
        start_time = float(input("Enter start time: ").strip())
        stop_time = float(input("Enter stop time: ").strip())
        startStopTime = (start_time, stop_time) 
    
    fp = os.path.sep

    root = ET.Element("inputData")
    length_path = os.path.join(MAFolder, '_MuscleAnalysis_Length.sto')
    muscle_length_elem = ET.SubElement(root, "muscleTendonLengthFile")
    muscle_length_elem.text = os.path.relpath(length_path, start=os.path.dirname(MAFolder))

    excitations_elem = ET.SubElement(root, "excitationsFile")
    excitations_elem.text = os.path.relpath(excitationsFile, start=os.path.dirname(MAFolder))
    
    # Add moment arms files 
    moment_arms = ET.SubElement(root, "momentArmsFiles")
    
    for dof in settings.DOFs:

        dof_path = os.path.join(MAFolder, f'_MuscleAnalysis_MomentArm_{dof}.sto')
        dof_elem = ET.SubElement(moment_arms, "momentArmsFile")
        dof_elem.set("dofName", dof)
        dof_elem.text = os.path.relpath(dof_path, start=os.path.dirname(MAFolder))  

    external_torques_elem = ET.SubElement(root, "externalTorquesFile")
    external_torques_elem.text = os.path.relpath(externalTorquesFile, start=os.path.dirname(MAFolder))

    motion_elem = ET.SubElement(root, "motionFile")
    motion_elem.text = os.path.relpath(motionFile, start=os.path.dirname(MAFolder))

    external_loads_elem = ET.SubElement(root, "externalLoadsFile")
    external_loads_elem.text = os.path.relpath(externalLoadsFile, start=os.path.dirname(MAFolder))

    startStop_elem = ET.SubElement(root, "startStopTime")
    startStop_elem.text = f"{startStopTime[0]} {startStopTime[1]}"
    
    savePath = os.path.join(os.path.dirname(MAFolder), 'inputData.xml')
    tree = ET.ElementTree(root)
    utils.save_pretty_xml(tree, savePath)

# Base run ceinms function
def ceinms_terminal(executable_path=None, setupXML_path=None):
    
    parentDir = os.path.dirname(setupXML_path)
    os.chdir(parentDir) # change wd to parent dir of setupXML 
    
    setupXML = ET.parse(setupXML_path).getroot()
    outputDirectory = setupXML.find("outputDirectory").text
    
    os.makedirs(outputDirectory, exist_ok=True) 
    
    print("Setup XML path:", setupXML_path)

    log_file_path = os.path.join(os.path.abspath(outputDirectory), 'out.txt')
    if os.path.exists(log_file_path): os.remove(log_file_path)
    
    try:
        ps_script = f'''
            $ErrorActionPreference = "Continue"
            $env:PATH = "{executable_path};$env:PATH"
            Set-Location "{parentDir}"
            & "{executable_path}" -S "{setupXML_path}"
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
                    print(line, end="")  # Print to terminal
                    log_file.write(line)
                    log_file.flush()

            process.wait()
        print(f"CEINMS optimise process finished!")
    except Exception as e:
        print(f"Error running CEINMS calibration: {e}")
        
    print(f"Log file saved to: {log_file_path}")

    # if Calibration commad
    # check if new calibrated model was created recently
    try:
        calibratedModelPath = setupXML.find('outputSubjectFile').text
        time_updated = os.path.getmtime(calibratedModelPath)
        if time_updated < os.path.getmtime(log_file_path):
            return False
        else:
            return True
    except Exception as e:
        print(f"Error checking calibrated model: {e}")
        return False
    
# CEINMS calibration functions
def calibrate(setupXML_path=None):
    
    if not setupXML_path:
        setupXML_path = input("Enter path to setup XML file: ").strip('"')
    
    os.chdir(os.path.dirname(setupXML_path)) # change wd to parent dir of setupXML (needed for CEINMS)
    
    setupXML = ET.parse(setupXML_path).getroot()
    outputDirectory = setupXML.find("outputDirectory").text
    
    os.makedirs(outputDirectory, exist_ok=True)
    
    print("Calibrating CEINMS model...")
    
    ceinms_terminal(executable_path=settings.CEINMS_CALIBRATION_EXE, 
                    setupXML_path=setupXML_path)

def calibrate_synergy_compare(setupXML_path=None, synergy_numbers: list = [3, 4, 5, 6]):
    if not setupXML_path:
        setupXML_path = input("Enter path to setup XML file: ").strip('"')
    
    base_dir = os.path.dirname(setupXML_path)
    
    for n in synergy_numbers:
        print(f"Calibrating with {n} synergies...")
        
        # Create a new setup XML with modified calibration config
        root = ET.parse(setupXML_path).getroot()

        outputDirectory = root.find("outputDirectory")
        outputDirectory.text = os.path.join(base_dir, f'calibrationOutput_synergies_{n}')
        
        utils.save_pretty_xml(ET.ElementTree(root), setupXML_path)

        # Load and modify calibration config and overwite cfg file
        calibrationFileTag = root.find('calibrationFile')
        calibrationCfgPath = calibrationFileTag.text
        calibrationCfgFullPath = os.path.join(base_dir, calibrationCfgPath)
        
        root_cfg = ET.parse(calibrationCfgFullPath).getroot()
        synergyTag = root_cfg.find('.//numberOfSynergies')
        synergyTag.text = str(n)

        tree = ET.ElementTree(root_cfg)
        utils.save_pretty_xml(tree, calibrationCfgFullPath)
        
        # Run calibration
        outputCalibration = calibrate(setupXML_path)
        
        # if new calibrated model is created, copy to outputDirectory with synergy number in filename
        calibratedModelPath = root.find('outputSubjectFile').text
        if outputCalibration:
            newCalibratedModelPath = os.path.join(outputDirectory, f"calibratedModel_synergies_{n}.xml")
            shutil.copy(calibratedModelPath, newCalibratedModelPath)

# CEINMS base exe function
def executable(setupXML_path=None):
    
    if not setupXML_path:
        setupXML_path = input("Enter path to setup XML file: ").strip('"')

    os.chdir(os.path.dirname(setupXML_path)) # change wd to parent dir of setupXML (needed for CEINMS)
    
    root = ET.parse(setupXML_path).getroot()
    outputDirectory = root.find("outputDirectory").text

    os.makedirs(outputDirectory, exist_ok=True)
    
    print("Running CEINMS executable...")
    ceinms_terminal(executable_path=settings.CEINMS_EXE, setupXML_path=setupXML_path)

def loop_gamma(setupXML_path=None, gammas: list = [1, 10, 100, 1000], ):
    if not setupXML_path:
        setupXML_path = input("Enter path to setup XML file: ").strip('"')
    
    if not loop_parameter:
        loop_parameter = input("Enter the parameter to loop over (e.g., 'betaMin'): ").strip()
    
    if not loop_values:
        values_str = input("Enter the values to loop over, separated by commas: ").strip()
        loop_values = [float(val) for val in values_str.split(',')]
    
    base_dir = os.path.dirname(setupXML_path)
    
    for value in loop_values:
        print(f"Running CEINMS with {loop_parameter} = {value}...")
        
        # Create a new setup XML with modified parameter
        root = ET.parse(setupXML_path).getroot()

        paramTag = root.find(f'.//{loop_parameter}')
        if paramTag is not None:
            paramTag.text = str(value)
        else:
            print(f"Parameter '{loop_parameter}' not found in setup XML.")
            continue

        # Update output directory to reflect current parameter value
        outputDirectory = root.find("outputDirectory")
        outputDirectory.text = os.path.join(base_dir, f'output_{loop_parameter}_{value}')
        
        new_setupXML_path = os.path.join(base_dir, f'setup_{loop_parameter}_{value}.xml')
        utils.save_pretty_xml(ET.ElementTree(root), new_setupXML_path)

        # Run CEINMS executable
        executable(setupXML_path=new_setupXML_path)
# Optimisation functions
def create_optimise_setupXML(ceinmsModelPath=None, 
                            inputDataFile=None,
                             calibrationCfgPath=None,
                             excitationGeneratorFilePath=None,
                             outputDirectory=None,
                             setupXMLPath=None):
    '''
    create CEINMS setup and configuration XML files for optimisation
    
    use settings.CEINMSParameters() for parameter ranges
    '''

    if not ceinmsModelPath:
        ceinmsModelPath = input("Enter path to CEINMS model file: ").strip('"')

    if not inputDataFile:
        inputDataFile = input("Enter path to input data file: ").strip('"')

    if not calibrationCfgPath:
        calibrationCfgPath = input("Enter path to calibration configuration file: ").strip('"')

    if not outputDirectory:
        outputDirectory = input("Enter path to output directory: ").strip('"')

    baseDir = os.path.dirname(calibrationCfgPath)
    root = ET.Element("ceinms")
    
    subjectFile = ET.SubElement(root, "subjectFile")
    subjectFile.text =  os.path.relpath(ceinmsModelPath, baseDir)
    
    inputData = ET.SubElement(root, "inputDataFile")
    inputData.text = os.path.relpath(inputDataFile, baseDir)
    
    executionFileTag = ET.SubElement(root, "executionFile")
    executionFileTag.text = os.path.relpath(calibrationCfgPath, baseDir)
    
    excitationGeneratorFile = ET.SubElement(root, "excitationGeneratorFile")
    excitationGeneratorFile.text = os.path.relpath(excitationGeneratorFilePath, baseDir)
    
    outputDirectoryTag = ET.SubElement(root, "outputDirectory")
    outputDirectoryTag.text = os.path.relpath(outputDirectory, baseDir)
    
    betaMinTag = ET.SubElement(root, "betaMin")
    betaMinTag.text = str(settings.CEINMSParameters().betaMin)
        
    betaMaxTag = ET.SubElement(root, "betaMax")
    betaMaxTag.text = str(settings.CEINMSParameters().betaMax)

    betaDeltaTag = ET.SubElement(root, "betaDelta")
    betaDeltaTag.text = str(settings.CEINMSParameters().betaDelta)

    gammaMinTag = ET.SubElement(root, "gammaMin")
    gammaMinTag.text = str(settings.CEINMSParameters().gammaMin)

    gammaMaxTag = ET.SubElement(root, "gammaMax")
    gammaMaxTag.text = str(settings.CEINMSParameters().gammaMax)

    gammaDeltaTag = ET.SubElement(root, "gammaDelta")
    gammaDeltaTag.text = str(settings.CEINMSParameters().gammaDelta)


    tree = ET.ElementTree(root)
    utils.save_pretty_xml(tree, setupXMLPath)
    
    print(f"Optimization setup XML saved to: {setupXMLPath}")

    # --- Create cfg file
    template_cfg = os.path.join(settings.SETUP_DIR, os.path.basename(settings.Inputs().CEINMS_OPTIMISE_CFG))
    cfgTemplate = ET.parse(template_cfg).getroot()
    
    # apply DOFs from CEINMS model
    ceinmsModel = ET.parse(ceinmsModelPath).getroot()
    dofSet = ceinmsModel.findall('.//dofSet')
    dofSet_cfg = cfgTemplate.findall('.//dofSet')[0]
    
    dofs = dofSet[0].findall('dof')
    dof_list = []
    for dof in dofs:
        dof_list.append(dof.find('name').text)
    
    dofSet_cfg.text = ' '.join(dof_list)
    
    # Lists to store muscle names
    synth_mtus = []
    adjust_mtus = []
    
    # Find all excitation elements
    exc_root = ET.parse(excitationGeneratorFilePath).getroot()
    
    mapping = exc_root.find('mapping')
    if mapping is not None:
        for excitation in mapping.findall('excitation'):
            muscle_id = excitation.get('id')

            # Check if excitation has input elements (non-empty)
            inputs = excitation.findall('input')
            if len(inputs) > 0:
                # Has EMG input - add to adjustMTUs
                adjust_mtus.append(muscle_id)
            else:
                # No EMG input - add to synthMTUs
                synth_mtus.append(muscle_id)
    
    # Sort the lists for consistent output
    synth_mtus.sort()
    adjust_mtus.sort()
    
    synthMTUsTag = cfgTemplate.findall('.//synthMTUs')[0]
    synthMTUsTag.text = ' '.join(synth_mtus)

    adjustMTUsTag = cfgTemplate.findall('.//adjustMTUs')[0]
    adjustMTUsTag.text = ' '.join(adjust_mtus)

    tree = ET.ElementTree(cfgTemplate)
    utils.save_pretty_xml(tree, calibrationCfgPath)
    print(f"Optimisation configuration XML saved to: {calibrationCfgPath}")
    
def optimise(setupXML_path=None):

    if not setupXML_path:
        setupXML_path = input("Enter path to setup XML file: ").strip('"')

    parentDir = os.path.dirname(setupXML_path)
    os.chdir(parentDir) # change wd to parent dir of setupXML (needed for CEINMS)
    
    root = ET.parse(setupXML_path).getroot()
    outputDirectory = root.find("outputDirectory").text

    # create output directory if it doesn't exist
    os.makedirs(outputDirectory, exist_ok=True)
    
    print("Optimizing CEINMS model...")
    ceinms_terminal(executable_path=settings.CEINMS_OPTIMISE_EXE, setupXML_path=setupXML_path)

# Plotting
def plot_ceinms_model_parameters(ceinmsModelPath=None):

    if not ceinmsModelPath:
        ceinmsModelPath = input("Enter path to optimised CEINMS model file: ").strip('"')

    def load_mtuSet(modelPath):
        root = ET.parse(modelPath).getroot()
        mtus = root.find('mtuSet').findall('mtu')
        
        # turn into DataFrame
        columns  = []
        for col in mtus[0].findall('*'): columns.append(col.tag)
        
        df = pd.DataFrame()
        for mtu in mtus:    
            name = mtu.find('name').text
            for col in columns:
                if col == 'name': continue
                if col not in df.columns:
                    df[col] = []
            for col in columns:
                if col == 'name': continue
                df.at[name, col] = float(mtu.find(col).text)
        
        return df

    mtuSet = load_mtuSet(ceinmsModelPath)
    muscle_names = mtuSet.index.tolist()
    parameters = mtuSet.columns.tolist()
    if len(parameters) == 10:    n_cols = 5
    else:                        n_cols = 4
    
    n_rows = (len(parameters) + n_cols - 1) // n_cols
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(10, n_rows*3))
    plt.suptitle(f'Optimised Muscle Parameters: {ceinmsModelPath}', fontsize=16)
    axs = axs.flatten()

    for i, param in enumerate(parameters):
        
        # convert to numeric
        mtuSet[param] = pd.to_numeric(mtuSet[param], errors='coerce')   
        
        # plot bars left leg in red and right leg in blue
        colors = ['red' if name.endswith('_l') else 'blue' for name in muscle_names]
        axs[i].bar(muscle_names, mtuSet[param], color=colors)
        axs[i].set_title(param)
        axs[i].set_xticklabels(muscle_names, rotation=90)
        
    # set legend left leg on top right leg on bottom
    red_patch = plt.Line2D([0], [0], color='red', lw=4, label='Left Leg')
    blue_patch = plt.Line2D([0], [0], color='blue', lw=4, label='Right Leg')
    plt.legend(handles=[red_patch, blue_patch], loc='upper right')

    # make figure fullsize and tight layout
    plt.gcf().set_size_inches(18, 10)
    plt.tight_layout()
    
    # save figure
    fig_path = ceinmsModelPath.replace('.xml', '_parameters.png')
    plt.savefig(fig_path)
    print(f"Muscle parameters plot saved to: {fig_path}")

def plot_compare_ceinms_models(uncalibratedModelPath=None,
                                  calibratedModelPath=None):
    
    def load_mtuSet(modelPath):
        root = ET.parse(modelPath).getroot()
        mtus = root.find('mtuSet').findall('mtu')
        
        # turn into DataFrame
        columns  = []
        for col in mtus[0].findall('*'): columns.append(col.tag)
        
        df = pd.DataFrame()
        for mtu in mtus:    
            name = mtu.find('name').text
            for col in columns:
                if col == 'name': continue
                if col not in df.columns:
                    df[col] = []
            for col in columns:
                if col == 'name': continue
                df.at[name, col] = float(mtu.find(col).text)
        
        return df

    if not uncalibratedModelPath:
        uncalibratedModelPath = input("Enter path to uncalibrated CEINMS model file: ").strip('"')
    
    if not calibratedModelPath:
        calibratedModelPath = input("Enter path to calibrated CEINMS model file: ").strip('"')
        
    
    mtuSet_uncalibrated = load_mtuSet(uncalibratedModelPath)
    mtuSet_calibrated = load_mtuSet(calibratedModelPath)
    
    muscle_names = mtuSet_uncalibrated.index.tolist()
    parameters = mtuSet_uncalibrated.columns.tolist()
    
    if len(parameters) == 10:    n_cols = 5
    else:                        n_cols = 4
    
    n_rows = (len(parameters) + n_cols - 1) // n_cols
    fig, axs = plt.subplots(n_rows, n_cols, figsize=(10, n_rows*3))
    
    
    plt.suptitle(f'Compare: uncalibrated vs calibrated', fontsize=16)
    axs = axs.flatten()

    for i, param in enumerate(parameters):
        
        # convert to numeric
        mtuSet_uncalibrated[param] = pd.to_numeric(mtuSet_uncalibrated[param], errors='coerce')   
        mtuSet_calibrated[param] = pd.to_numeric(mtuSet_calibrated[param], errors='coerce')
        
        # plot bars left leg in red and right leg in blue
        colors = ['red' if name.endswith('_l') else 'blue' for name in muscle_names]
        if param in ['optimalFibreLength', 'pennationAngle', 'tendonSlackLength']:
            diff = mtuSet_calibrated[param] - mtuSet_uncalibrated[param]
            axs[i].bar(muscle_names, diff, color=colors)
            axs[i].set_title(f'Difference in {param} (Calibrated - Uncalibrated)')
            axs[i].set_xticklabels(muscle_names, rotation=90)
        else:            
            axs[i].bar(muscle_names, mtuSet_calibrated[param], color=colors)
            axs[i].set_title(param)
            axs[i].set_xticklabels(muscle_names, rotation=90)
            
    # set legend left leg on top right leg on bottom
    red_patch = plt.Line2D([0], [0], color='red', lw=4, label='Left Leg')
    blue_patch = plt.Line2D([0], [0], color='blue', lw=4, label='Right Leg')
    plt.legend(handles=[red_patch, blue_patch], loc='upper right')

    # make figure fullsize and tight layout
    plt.gcf().set_size_inches(18, 10)
    plt.tight_layout()
    
    # save figure
    fig_path = calibratedModelPath.replace('.xml', '_vs_uncalibrated.png')
    plt.savefig(fig_path)
    print(f"Muscle parameters plot saved to: {fig_path}")

def plot_moments_calibration_results(momentResultsCSV=None):
    
    if not momentResultsCSV:
        momentResultsCSV = input("Enter path to moment calibration results CSV file: ").strip('"')

    moments_df = utils.load_any_data_file(momentResultsCSV)
    columns = moments_df.columns.tolist()
    data_columns = [col for col in columns if col != 'time']
    data_columns.sort()
    
    # get dof names by removing '_id' from id_columns
    dof_pairs = []
    for col in data_columns:
        moment_col = col + '_id'
        if moment_col in data_columns:
            dof_pairs.append((col, moment_col))

    n_dofs = len(dof_pairs)
    ncols = 2  # 2 columns for better layout
    nrows = int(np.ceil(n_dofs / ncols))
    
    # Create the figure and subplots
    fig, axes = plt.subplots(nrows, ncols, figsize=(15, 4*nrows))
    if n_dofs == 1:
        axes = [axes]
    elif nrows == 1:
        axes = axes.reshape(1, -1)
    axes = axes.flatten()
    
    # Plot each DOF pair
    for i, (dof, dof_id) in enumerate(dof_pairs):
        ax = axes[i]
        
        # Plot the DOF angle
        line1 = ax.plot(moments_df['time'], moments_df[dof], 'b-', linewidth=2, label=f'ceinms)')
        line2 = ax.plot(moments_df['time'], moments_df[dof_id], 'r-', linewidth=2, label=f'inverse dynamics')

        # Set labels and title
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Moment (Nm)')
        ax.set_title(dof)
        ax.tick_params(axis='y')
        ax.grid(True, alpha=0.3)
        
        # Add legend (only on first subplot to avoid clutter)
        if i == 0:
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            ax.legend(lines, labels, loc='upper right')
    
    # Hide any unused subplots
    for i in range(n_dofs, len(axes)):
        axes[i].set_visible(False)
    
    # Adjust layout
    plt.tight_layout()
    plt.suptitle('DOF Angles and Moments Comparison', fontsize=16, y=1.02)
    
    # Save the figure
    savePath = momentResultsCSV.replace('.csv', '.png')
    plt.savefig(savePath, dpi=300, bbox_inches='tight')
    print(f"DOF comparison plot saved as '{savePath}'")

    return fig, axes, dof_pairs
  
def plot_ceinms_calibration_results(calibrationOutputDir=None):

    if not calibrationOutputDir:
        calibrationOutputDir = input("Enter path to calibration output directory: ").strip('"')

    # find all files ending with _calibrationResults.sto
    result_files = os.listdir(calibrationOutputDir)
    result_files = [os.path.join(calibrationOutputDir, f) for f in result_files if f.endswith('.csv')]
    Muscle_Groups = settings.Muscle_Groups
    for result_file in result_files:
        data = utils.load_any_data_file(result_file)
        
        muscle_names = [col for col in data.columns if col != 'time']

        n_muscle_groups = len(Muscle_Groups)
        fig, axs = plt.subplots(n_muscle_groups, 1, figsize=(10, n_muscle_groups*3))
        plt.suptitle(f'Calibration Results: {os.path.basename(result_file)}', fontsize=16)
        for i, (muscle_group, muscles) in enumerate(Muscle_Groups.items()):
            ax = axs[i] if n_muscle_groups > 1 else axs
            for muscle in muscles:
                if muscle in muscle_names:
                    ax.plot(data['time'], data[muscle], label=muscle)
            ax.set_title(f'Calibration Results for Muscle Group: {muscle_group}')
            
            # if not last subplot, remove x labels
            if i < n_muscle_groups - 1:
                ax.set_xticklabels([])
            else:
                ax.set_xlabel('Time (%)')
                
            ax.legend()
            
        
        # save figure
        fig_path = result_file.replace('.csv', '.png')
        plt.savefig(fig_path)
        print(f"Calibration results plot saved to: {fig_path}")
        plt.close()

def plot_optimisation_results(optimisationOutputDir=None):

    if not optimisationOutputDir:
        optimisationOutputDir = input("Enter path to optimisation output directory: ").strip('"')

    # find all files ending with _optimisationResults.sto
    result_files = os.listdir(optimisationOutputDir)
    result_files = [os.path.join(optimisationOutputDir, f) for f in result_files if f.endswith('.sto')]
    Muscle_Groups = settings.Muscle_Groups
    for result_file in result_files:
        data = utils.load_any_data_file(result_file)
        
        muscle_names = [col for col in data.columns if col != 'time']

        n_muscle_groups = len(Muscle_Groups)
        fig, axs = plt.subplots(n_muscle_groups, 1, figsize=(10, n_muscle_groups*3))
        plt.suptitle(f'Optimisation Results: {os.path.basename(result_file)}', fontsize=16)
        for i, (muscle_group, muscles) in enumerate(Muscle_Groups.items()):
            ax = axs[i] if n_muscle_groups > 1 else axs
            for muscle in muscles:
                if muscle in muscle_names:
                    ax.plot(data['time'], data[muscle], label=muscle)
            ax.set_title(f'Optimisation Results for Muscle Group: {muscle_group}')
            
            # if not last subplot, remove x labels
            if i < n_muscle_groups - 1:
                ax.set_xticklabels([])
            else:
                ax.set_xlabel('Time (%)')
                
            ax.legend()
            
        
        # save figure
        fig_path = result_file.replace('.sto', '.png')
        plt.savefig(fig_path)
        print(f"Optimisation results plot saved to: {fig_path}")
        plt.close()

def plot_experimental_vs_ceinms(emgFile=None,        
                                ceinmsExcitationsFile=None,excitationGeneratorFile=None,externalMomentsFile=None, ceinmsTorquesFile=None):

    if not emgFile:
        emgFile = input("Enter path to EMG data file: ").strip('"')

    if not ceinmsExcitationsFile:
        ceinmsExcitationsFile = input("Enter path to CEINMS excitations file: ").strip('"')
    
    if not excitationGeneratorFile:
        excitationGeneratorFile = input("Enter path to excitation generator file: ").strip('"')
    
    if not externalMomentsFile:
        externalMomentsFile = input("Enter path to external moments data file: ").strip('"')

    if not ceinmsTorquesFile:
        ceinmsTorquesFile = input("Enter path to CEINMS torques data file: ").strip('"')

    emg_data = utils.load_any_data_file(emgFile)
    ceinms_data = utils.load_any_data_file(ceinmsExcitationsFile)
    
    ceinms_time_range  = [ceinms_data['time'].iloc[0],ceinms_data['time'].iloc[-1]]
    emg_data = emg_data[(emg_data['time'] >= ceinms_time_range[0]) & (emg_data['time'] <= ceinms_time_range[1])]
    
    emg_time_range  = [emg_data['time'].iloc[0],emg_data['time'].iloc[-1]]

    # time normalise both datasets to the same length
    emg_data = utils.time_normalise_df(emg_data)
    ceinms_data = utils.time_normalise_df(ceinms_data)
    
    emg_mapping = ET.parse(excitationGeneratorFile).getroot().find('mapping')

    muscle_mapping = {}
    for excitation in emg_mapping.findall('excitation'):
        muscle_id = excitation.get('id')
        input_elems = excitation.findall('input')
        if len(input_elems) > 0:
            for input_elem in input_elems:
                signal = input_elem.text
                if signal not in muscle_mapping:
                    muscle_mapping[signal] = []
                muscle_mapping[signal].append(muscle_id)
    
    # -- Plot EMG vs CEINMS excitations -- #     
    n_muscles = len(muscle_mapping)
    fig, axs = plt.subplots(n_muscles, 1, figsize=(10, n_muscles*3))
    plt.suptitle(f'EMG vs CEINMS Excitations', fontsize=16)
    for i, (signal, muscles) in enumerate(muscle_mapping.items()):
        ax = axs[i] if n_muscles > 1 else axs
        line_emg = ax.plot(emg_data['time'], emg_data[signal], label=signal, color='blue')
        lines_ceinms = []   
        lineStyles = ['-', '--', '-.', ':','-', '--', '-.', ':']
        for j, muscle in enumerate(muscles):
            if muscle in ceinms_data.columns:
                r2 = utils.rsquared(emg_data[signal], ceinms_data[muscle])
                range_signal = emg_data[signal].max() - emg_data[signal].min()
                rmse = utils.rmse(emg_data[signal], ceinms_data[muscle])
                rmse_percent = (rmse / range_signal) * 100 if range_signal != 0 else 0
                lines_ceinms.append(ax.plot(ceinms_data['time'],ceinms_data[muscle], 
                                            linestyle=lineStyles[j % len(lineStyles)],
                                            label=f'{muscle} (R²: {r2:.2f}, RMSE: {rmse:.2f}/{rmse_percent:.0f}%)', color='red'))
                ax.set_ylabel('Excitation')
                if i < n_muscles - 1:
                    ax.set_xticklabels([])
                else:
                    ax.set_xlabel('Time (%)')
            else:
                print(f"Muscle {muscle} not found in CEINMS excitations data.")
        
        # legend with all lines
        handles = [line_emg[0]] + [line[0] for line in lines_ceinms]
        labels = [signal] + [f'{muscle} (R²: {utils.rsquared(emg_data[signal], ceinms_data[muscle]):.2f}, RMSE: {utils.rmse(emg_data[signal], ceinms_data[muscle]):.2f})' for muscle in muscles if muscle in ceinms_data.columns]
        ax.legend(handles, labels)
    
    # save figure
    ext = os.path.splitext(ceinmsExcitationsFile)[1]
    fig_path = ceinmsExcitationsFile.replace(ext, 'vs_emg.png')
    plt.savefig(fig_path)
    print(f"EMG vs CEINMS excitations plot saved to: {fig_path}")
    plt.close()

    # -- Plot external moments vs CEINMS torques -- #
    
    ext_moments_data = utils.load_any_data_file(externalMomentsFile)
    ceinms_torques_data = utils.load_any_data_file(ceinmsTorquesFile)
    
    # allign times and time normalise
    time_range_torques  = [ceinms_torques_data['time'].iloc[0],ceinms_torques_data['time'].iloc[-1]]
    ext_moments_data = ext_moments_data[(ext_moments_data['time'] >= time_range_torques[0]) & (ext_moments_data['time'] <= time_range_torques[1])]

    ext_moments_data = utils.time_normalise_df(ext_moments_data)
    ceinms_torques_data = utils.time_normalise_df(ceinms_torques_data)

    dof_names = [col for col in ceinms_torques_data.columns if col != 'time']
    
    n_dofs = len(dof_names)
    fig, axs = plt.subplots(n_dofs, 1, figsize=(10, n_dofs*3))
    plt.suptitle(f'External Torques vs CEINMS Torques', fontsize=16)
    
    for i, dof in enumerate(dof_names):
        ax = axs[i] if n_dofs > 1 else axs
        r2 = utils.rsquared(ext_moments_data[dof + '_moment'], ceinms_torques_data[dof])
        range_moments = ext_moments_data[dof + '_moment'].max() - ext_moments_data[dof + '_moment'].min()        
        rmse = utils.rmse(ext_moments_data[dof + '_moment'], ceinms_torques_data[dof])
        rmse_percent = (rmse / range_moments) * 100 if range_moments != 0 else 0
        line_ext = ax.plot(ext_moments_data[dof + '_moment'], label=f'External Moment', color='blue')
        line_cei = ax.plot(ceinms_torques_data[dof], label=f'CEINMS Torque (R²: {r2:.2f}, RMSE: {rmse:.2f}/{rmse_percent:.0f}%)', color='red')
        ax.set_title(f'{dof}')
        ax.set_ylabel('Moment (Nm)')
        if i < n_dofs - 1:
            ax.set_xticklabels([])
        else:
            ax.set_xlabel('Time (%)')
        ax.legend()
    
    ext = os.path.splitext(ceinmsTorquesFile)[1]
    fig_path = ceinmsTorquesFile.replace(ext, 'vs_external_torques.png')
    plt.savefig(fig_path)
    print(f"External torques vs CEINMS torques plot saved to: {fig_path}")
    plt.close()



if __name__ == "__main__":
    
    LocalFuncs = [f for f in dir() if callable(globals()[f])]
    print("Available commands:", LocalFuncs)

    # Command loop
    while True:
        command = input("Enter command: ")

        if not command in LocalFuncs:
            print("Invalid command. Please try again.")
            continue

        try:
            globals()[command]()
        except Exception as e:
            print(f"Error executing {command}: {e}")
        
        