import os
import subprocess
import settings
import xml.etree.ElementTree as ET
import opensim as osim
import utils

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
    ET.SubElement(uncalibrated, "additionalInfo").text = "TendonSlackLength and OptimalFibreLength scaled with Winby-Modenese"
    
    # Add opensimModelFile reference
    ET.SubElement(root, "opensimModelFile").text = osimModelPath

    # Create the XML tree and save
    tree = ET.ElementTree(root)
    
    if not outputCEINMSModelPath:
        outputCEINMSModelPath = osimModelPath.replace('.osim', '.xml')
        
    utils.save_pretty_xml(tree, outputCEINMSModelPath)

    print(f"CEINMS subject file created: {outputCEINMSModelPath}")

def create_excitation_mapping(osim_model_path=None, emg_path=None, save_path=None):
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
        osim_model_path = settings.osimModelPath
        
    if not emg_path:
        emg_path = settings.emgPath
        
    if not save_path:
        save_path = settings.excitationGeneratorPath
    
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
    utils.save_pretty_xml(tree, save_path)
    print(f"XML saved to {save_path}")

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
    
    if not osimModelPath: 
        osimModelPath = settings.osimModelPath
        
    if not inputPaths:
        inputPaths = settings.inputPaths

    if not outputPath:
        outputPath = input("Enter path to save the calibration configuration XML file: ")
        
    # make paths relative to outputPath
    outputPathParent = os.path.dirname(outputPath)
    inputPaths = [os.path.relpath(p, outputPathParent) for p in inputPaths]

    # Create root element
    root = ET.Element("calibration")
        
    optimiser_types = {'earlyStopping': {
        'minImprovement': 0.1,
        'patience': 20
    }, 'learningRateDecay': {
        'enabled': True,    
        'patience': 50,
        'minDelta': 1e-6
    }}
    
    model = osim.Model(osimModelPath)
    muscles = model.getMuscles()
    muscle_names = [muscles.get(i).getName() for i in range(muscles.getSize())]
    
    forceSet = model.getForceSet()
    
    muscleGroups = {}
    for i in range(forceSet.getNumGroups()):
        group = forceSet.getGroup(i)
        group_name = group.getName()
        members = group.getMembers()
        breakpoint()
        for j in range(members.getSize()):
            breakpoint()
            muscles = members.get(j)
    
    # Merge with provided config
    settings = {'optimiser': {
                          'hybridCalibration': True,
                          'learningRate': 0.02,
                          'maxIterations': 1000,
                          'numberOfSynergies': 6,
                          'earlyStopping': optimiser_types['earlyStopping'],
                          'tendon': 'elastic',
                          'numberOfSynergies': 6
               },
                'calibrationTargets': {
                    'parametersToCalibrate': {
                        'c1': '-0.95 -0.05',
                        'c2': '-0.95 -0.05',
                        'shapefactor': '-2.999 -0.001',
                        'optimalFiberLength': '0.95 1.05',
                        'tendonSlackLength': '0.95 1.05',
                        'strengthCoefficient': '0.5 3.5',
                        'muscleGroups': muscles
                    },
                    'objectiveFunctions': {
                        'MomentError': {
                            'targets': 'all',
                            'weight': '1'
                        },
                        'Penalty': {
                            'targetType': 'normalisedFibreLength',
                            'weight': '1000',
                            'exponent': '2',
                            'range': [0.5, 1.5]
                        },
                        'Penalty': {
                            'targetType': 'tendonStrain',
                            'weight': '1000',
                            'exponent': '2',
                            'range': [0.0, 0.5]
                        },
                        'ExcitationsSquared': {
                            'weight': '1'
                        },
                        'SynergyExtraction': {
                            'mseWeight': '100',
                            'range': [0.0, 1.0],
                            'rangeExponent': '2',
                            'rangeWeight': '1000'
                        }
                    },
                    'muscles': 'all'
                },
                'trialSet': ' '.join(inputPaths)
    }
    
    for key, value in settings.items():
        elem = ET.SubElement(root, key)
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                subelem = ET.SubElement(elem, subkey)
                subelem.text = str(subvalue)
        else:
            elem.text = str(value)
    
    tree = ET.ElementTree(root)
    utils.save_pretty_xml(tree, outputPath)

    return root

def create_calibrationSetupXML(calibrationCfgPath=None, outputPath=None):

    if not calibrationCfgPath:
        calibrationCfgPath = input("Enter path to calibration config file: ").strip('"')

    root = ET.Element("ceinmsCalibration")

    subjectFile = ET.SubElement(root, "subjectFile")
    subjectFile.text = settings.Outputs().CEINMS_UNCALIBRATED_MODEL
    
    excitationGeneratorFile = ET.SubElement(root, "excitationGeneratorFile")
    excitationGeneratorFile.text = settings.excitationGeneratorPath
    
    calibrationFile = ET.SubElement(root, "calibrationFile")
    calibrationFile.text = settings.SetupFiles().CEINMS_CALIBRATION_CFG
    
    outputSubjectFile = ET.SubElement(root, "outputSubjectFile")
    outputSubjectFile.text = settings.Outputs().CEINMS_CALIBRATED_MODEL
    
    outputDirectory = ET.SubElement(root, "outputDirectory")
    outputDirectory.text = settings.Outputs().CEINMS_CALIBRATION_OUTPUT

    tree = ET.ElementTree(root)
    utils.save_pretty_xml(tree, outputPath)

def create_input_data(MAFolder=None, excitationsFile=None, motionFile=None, externalTorquesFile=None, 
                      externalLoadsFile=None, startStopTime=None):
    
    if not MAFolder:
        MAFolder = settings.Outputs().MA
        
    if not excitationsFile:
        excitationsFile = settings.Inputs().CEINMS_EXCITATIONS
    
    fp = os.path.sep

    root = ET.Element("inputData")
    muscle_length_elem = ET.SubElement(root, "muscleTendonLengthFile")
    muscle_length_elem.text = str(MAFolder) + fp + '_MuscleAnalysis_Length.sto'

    excitations_elem = ET.SubElement(root, "excitationsFile")
    excitations_elem.text = excitationsFile
    
    # Add moment arms files 
    moment_arms = ET.SubElement(root, "momentArmsFiles")
    
    for dof in settings.DOFs:
        dof_elem = ET.SubElement(moment_arms, "momentArmFile")
        dof_elem.set("dofName", dof)
        dof_elem.text = str(MAFolder) + fp + f'_MuscleAnalysis_MomentArm_{dof}.sto'

    external_torques_elem = ET.SubElement(root, "externalTorquesFile")
    external_torques_elem.text = settings.Outputs().ID
    
    motion_elem = ET.SubElement(root, "motionFile")
    motion_elem.text = settings.Outputs().IK
    
    startStop_elem = ET.SubElement(root, "startStopTime")
    startStop_elem.text = f"{timeRange[0]} {timeRange[1]}"
    
    savePath = os.path.join(trialPath, 'inputData.xml')
    tree = ET.ElementTree(root)
    utils.save_pretty_xml(tree, savePath)

def calibrate(setupXML_path=None):
    
    if not setupXML_path:
        setupXML_path = input("Enter path to setup XML file: ").strip('"')
    
    os.chdir(os.path.dirname(setupXML_path)) # change wd to parent dir of setupXML (needed for CEINMS)
    
    root = ET.parse(setupXML_path).getroot()
    outputDirectory = root.find("outputDirectory").text
    
    os.makedirs(outputDirectory, exist_ok=True)
    
    print("Calibrating CEINMS model...")
    
    print("Setup XML path:", setupXML_path)

    command = f"{str(settings.CEINMS_CALIBRATION_EXE)} -S {str(setupXML_path)}"
    
    if not os.path.exists(settings.CEINMS_CALIBRATION_EXE):
        raise FileNotFoundError(f"CEINMS calibration executable not found at {settings.CEINMS_CALIBRATION_EXE}")

    log_file_path = os.path.join(os.path.abspath(outputDirectory), 'calibration.log')

    cmd_with_redirect = f"{command} 2>&1 | Tee-Object -FilePath '{log_file_path}'; exit"
    
    print(f"Running command: {command}")
    try:
        
        process = subprocess.Popen(
            ["powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", cmd_with_redirect],
            creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        process.wait()
        print(f"CEINMS calibration process finished!")
        print(f"Log file saved to: {log_file_path}")
    except Exception as e:
        print(f"Error running CEINMS calibration: {e}")

def optimise(setupXML_path=None):

    if not setupXML_path:
        setupXML_path = input("Enter path to setup XML file: ").strip('"')

    os.chdir(os.path.dirname(setupXML_path)) # change wd to parent dir of setupXML (needed for CEINMS)
    
    root = ET.parse(setupXML_path).getroot()
    outputDirectory = root.find("outputDirectory").text

    os.makedirs(outputDirectory, exist_ok=True)
    
    print("Optimizing CEINMS model...")
    print("Setup XML path:", setupXML_path)

    command = f"{str(settings.CEINMS_OPTIMISE_EXE)} -S {str(setupXML_path)}"

    log_file_path = os.path.join(os.path.abspath(outputDirectory), 'calibration.log')

    cmd_with_redirect = f"{command} 2>&1 | Tee-Object -FilePath '{log_file_path}'; exit"
    
    print(f"Running command: {command}")
    try:
        
        process = subprocess.Popen(
            ["powershell", "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", cmd_with_redirect],
            creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        process.wait()
        print(f"CEINMS optimise process finished!")
    except Exception as e:
        print(f"Error running CEINMS calibration: {e}")

if __name__ == "__main__":
    
    LocalFuncs = [f for f in dir() if callable(globals()[f])]
    print("Available commands:", LocalFuncs)
    
    os.chdir(settings.trialPath)

    while True:
        command = input("Enter command: ")

        if not command in LocalFuncs:
            print("Invalid command. Please try again.")
            continue

        for func_name in LocalFuncs:
            if command == func_name:
                globals()[func_name]()
                break
        
        