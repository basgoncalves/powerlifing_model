import shutil
import time
from tkinter import filedialog, messagebox, simpledialog
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
import sys
import pandas as pd
import re
# import c3d
import xml.etree.ElementTree as ET
import xml.dom.minidom
import os
import opensim as osim

import tk

MODULE_DIR = os.path.dirname(os.path.abspath(__file__))

def print_to_log(message):
    """
    Prints a message to the console and logs it to a file.
    
    Args:
        message (str): The message to print and log.
    """
    timestamp = time.strftime('%d.%m.%Y_%H:%M:%S', time.localtime()) + f":{int((time.time() % 1) * 1000):03d}"
    print(f'{timestamp} {message}')
    with open(MODULE_DIR + '\\log.txt', 'a') as log_file:
        log_file.write(f'{timestamp}: {message}\n')

def rel_path(path, relative_to):
    """
    Returns the relative path from the given path to the code directory.
    
    Args:
        path (str): The path to convert.
        relative_to (str): The base path to which the relative path is calculated.
        
    Returns:
        str: The relative path.
    """
    return os.path.relpath(path, relative_to)

def check_path(path, create=False, isdir=False):
    """Check if a path exists and is a directory."""
    if not os.path.exists(path):        
        if create:
            try:
                os.makedirs(path)
                print("[INFO] Created directory:", path)
            except Exception as e:
                print("[ERROR] Could not create directory:", path, "Error:", e)
        else:
            print("[ERROR] Path does not exist:", path)
    if isdir and not os.path.isdir(path):
        print("[ERROR] Path is not a directory:", path)

    return path, os.path.isdir(path)

def load_c3d(path=None, output=0):
    """
    Load a .c3d file into a pandas DataFrame.

    Args:
        path (str): The path to the .c3d file. If None, prompts for input.
        output (int): If 1, prints the columns of the DataFrame.

    Returns:
        pd.DataFrame: The loaded data from the .c3d file.
    """
    
    if not check_path(path):
        path = input("Please provide the path to the .c3d file: ")

    try:
        reader = c3d.Reader(open(path, 'rb'))
        
        return reader 
    except Exception as e:
        print(f"Error: Could not read the file at {path}. Please check the file format and try again.")
        print(f"Details: {e}")
    
def load_trc(path=None, output=0):
    
    if not check_path(path):
        path = input("Please provide the path to the .trc file: ")

    # find line with '#Frame' to skip the header
    try:
        with open(path, 'r') as file:
            for i, line in enumerate(file):
                if 'Frame#' in line:
                        break
    except:
        print(f"Error: Could not read the file at {path}. Please check the path and try again.")
        return None
        
    # read headers in line i
    try:
        with open(path, 'r') as file:
            headers = file.readlines()[i].strip().split('\t')
    except:
        print(f"Error: Could not read the file at {path}. Please check the path and try again.")
        return None

    # read the file into a pandas DataFrame, skipping the header
    try:
        data = pd.read_csv(path, sep= '\s+', header=i+1, index_col=False)
        # add the headers to the DataFrame above the data
        data.columns = headers
        
    except Exception as e:
        print(f"Error: Could not read the file at {path}. Please check the file format and try again.")
        print(f"Details: {e}")
        return None

    if output == 1: print(data.columns)

    return data

def load_mot(path=None, output=0):
    """
    Load a .mot file into a pandas DataFrame.

    Args:
        path (str): The path to the .mot file. If None, prompts for input.
        output (int): If 1, prints the columns of the DataFrame.

    Returns:
        pd.DataFrame: The loaded data from the .mot file.
    """
    
    if not check_path(path):
        path = input("Please provide the path to the .mot file: ")

    # find line with 'endheader' to skip the header
    try:
        with open(path, 'r') as file:
            for i, line in enumerate(file):
                if 'endheader' in line:
                        break
    except:
        print(f"Error: Could not read the file at {path}. Please check the path and try again.")
        return None
    
    # read the file into a pandas DataFrame, skipping the header
    try:
        if path.endswith('.sto'):
            data = pd.read_csv(path, sep= '\s+', header=i+1)
        else:
            data = pd.read_csv(path, sep= '\s+', header=i-1)
        
        # check if header is non numeric or empty
        if data.columns[0].isdigit() or data.columns[0] == '':
            print(f"Warning: The first column of the file {path} is numeric or empty. This may cause issues with the data structure.")
        
    except Exception as e:
        print(f"Error: Could not read the file at {path}. Please check the file format and try again.")
        print(f"Details: {e}")
        return None

    if output == 1: print(data.columns)

    return data

def load_sto(path=None, output=0):
    """
    Load a .sto file into a pandas DataFrame.

    Args:
        path (str): The path to the .sto file. If None, prompts for input.
        output (int): If 1, prints the columns of the DataFrame.

    Returns:
        pd.DataFrame: The loaded data from the .sto file.
    """
    
    if not check_path(path):
        path = input("Please provide the path to the .sto file: ")

    # find line with 'endheader' to skip the header
    try:
        with open(path, 'r') as file:
            for i, line in enumerate(file):
                if 'endheader' in line:
                        break
    except:
        print(f"Error: Could not read the file at {path}. Please check the path and try again.")
        return None

    # read the file into a pandas DataFrame, skipping the header
    try:
        columns = []
        offset = -3
        while 'time' not in columns:
            try:    
                if path.__contains__('force'):
                    data = pd.read_csv(path, sep= '\s+', header=i-3)
                    columns = data.columns
                else:
                    data = pd.read_csv(path, sep= '\s+', header=i+offset)
                    columns = data.columns
                
                offset += 1
            except pd.errors.ParserError:
                offset += 1
                
    except Exception as e:
        print(f"Error: Could not read the file at {path}. Please check the file format and try again.")
        print(f"Details: {e}")
        return None

    if output == 1: print(data.columns)

    return data

def load_grf_mot(path=None, output=0):
    
    if not check_path(path):
        path = input("Please provide the path to the .mot file: ")

    # find line with 'endheader' to skip the header
    try:
        with open(path, 'r') as file:
            for i, line in enumerate(file):
                if 'endheader' in line:
                        break
    except:
        print(f"Error: Could not read the file at {path}. Please check the path and try again.")
        return None

    # read the file into a pandas DataFrame, skipping the header
    try:
        data = pd.read_csv(path, sep= '\s+', header=i+1)
    except Exception as e:
        print(f"Error: Could not read the file at {path}. Please check the file format and try again.")
        print(f"Details: {e}")
        return None

    if output == 1: print(data.columns)

    return data

def load_data_file(file_path):
    """
    Loads the motion capture data file into a pandas DataFrame.

    This function reads the header to extract metadata and then loads the
    actual data into a structured DataFrame.

    Args:
        file_path (str): The path to the data file.

    Returns:
        tuple: A tuple containing:
            - pd.DataFrame: The loaded data.
            - dict: A dictionary with the file's metadata.
    """
    metadata = {}
    header_lines = []
    
    # Read the header part of the file first to extract metadata
    with open(file_path, 'r') as f:
        for i in range(5):  # First 5 lines are metadata or headers
            line = f.readline().strip()
            header_lines.append(line)
            if i < 2: # The first two lines contain key-value metadata
                parts = line.split('\t')
                for j in range(0, len(parts), 2):
                    if j + 1 < len(parts) and parts[j]:
                        metadata[parts[j]] = parts[j+1]

    # The 4th line contains the main column headers (FHD, RBHD, etc.)
    # The 5th line contains the sub-column headers (X1, Y1, etc.)
    main_headers = re.split(r'\s+', header_lines[3].strip())[2:] # Skip first two empty items
    sub_headers = re.split(r'\s+', header_lines[4].strip())[2:] # Skip first two items

    # Create a MultiIndex (hierarchical column names) for the DataFrame
    # This matches your file's structure (e.g., FHD -> X1, Y1, Z1)
    header_tuples = []
    i = 0
    for main_header in main_headers:
        if main_header: # Check if it's not an empty string
            # Each main header corresponds to a set of sub-headers (e.g., X, Y, Z coordinates)
            num_sub_headers = 3 # Assuming X, Y, Z for markers. Adjust if needed.
            for j in range(num_sub_headers):
                header_tuples.append((main_header, sub_headers[i]))
                i += 1

    # Define the column names for the first two columns
    final_column_names = [('Frame', '#'), ('Time', '')] + header_tuples

    # Load the actual data, skipping the header rows
    data = pd.read_csv(
        file_path,
        sep='\t',        # Data is separated by tabs
        header=None,     # We are providing our own column names
        skiprows=6,      # Skip the metadata and header lines we already processed
        engine='python'  # Use python engine for more flexibility with separators
    )
    
    # Assign the hierarchical column names to the DataFrame
    data.columns = pd.MultiIndex.from_tuples(final_column_names)

    return data, metadata

def load_any_data_file(file_path):
    """
    Loads any data file (TRC, MOT, STO, C3D) into a pandas DataFrame.

    Args:
        file_path (str): The path to the data file.

    Returns:
        pd.DataFrame: The loaded data.
    """
    if file_path.endswith('.trc'):
        return load_trc(file_path)
    
    elif file_path.endswith('.mot'):
        return load_mot(file_path)
    
    elif file_path.endswith('.sto'):
        return load_sto(file_path)
    
    elif file_path.endswith('.c3d'):
        return load_c3d(file_path)
    
    elif file_path.endswith('.txt') or file_path.endswith('.csv'):
        # Assuming these are plain text files with tab-separated values
        return pd.read_csv(file_path, sep='\t', header=0)
    
    elif file_path.endswith('.xml'):
        # For XML files, we can use the XML_tools module to read them
        tree = ET.parse(file_path)
        if tree is not None:
            return pd.DataFrame([elem.attrib for elem in tree.findall('.//')])
        else:
            raise ValueError(f"Could not read XML file: {file_path}")
    else:
        try:
            # Try to read as a generic text file
            with open(file_path, 'r') as f:
                data = f.readlines()
            # Assuming the first line is a header
            header = data[0].strip().split('\t')
            # Load the rest of the data into a DataFrame
            data = [line.strip().split('\t') for line in data[1:]]
            return pd.DataFrame(data, columns=header)
        
        except Exception as e:
            print(f"Error: Could not read the file at {file_path}. Please check the file format and try again.")
            print(f"Details: {e}")
            

def save_data_file(file_path, data, metadata):
    """
    Saves the DataFrame back to a file in the original format.

    Args:
        file_path (str): The path where the file will be saved.
        data (pd.DataFrame): The DataFrame to save.
        metadata (dict): The metadata to write to the header.
    """
    with open(file_path, 'w') as f:
        # Write metadata lines
        # This part reconstructs the first two header lines from the metadata dictionary
        # It's a bit manual to match the format exactly.
        f.write(f"PathFileType\t4\t(X/Y/Z)\t{metadata.get('PathFileType', '')}\n")
        f.write(f"DataRate\t{metadata.get('DataRate', '')}\tCameraRate\t{metadata.get('CameraRate', '')}\tNumFrames\t{metadata.get('NumFrames', '')}\tNumMarkers\t{metadata.get('NumMarkers', '')}\tUnits\t{metadata.get('Units', '')}\tOrigDataRate\t{metadata.get('OrigDataRate', '')}\tOrigDataStartFrame\t{metadata.get('OrigDataStartFrame', '')}\tOrigNumFrames\t{metadata.get('OrigNumFrames', '')}\n")
        f.write('\n') # The empty line
        
        # Reconstruct the column headers
        main_headers = data.columns.get_level_values(0)
        sub_headers = data.columns.get_level_values(1)
        
        # Write main headers line
        f.write("Frame#\tTime\t")
        unique_main_headers = main_headers.unique()
        # This logic ensures each main header is printed once and padded correctly
        header_line = ""
        last_main = ""
        for main in main_headers[2:]: # Skip Frame and Time
            if main != last_main:
                header_line += f"{main}\t\t\t" # Assuming 3 sub-columns, hence 3 tabs
                last_main = main
        f.write(header_line.strip() + '\n')

        # Write sub-headers line
        f.write("\t\t") # Align with the data columns
        f.write('\t'.join(sub_headers[2:]) + '\n')
        f.write('\n') # The final empty line before data

    # Append the data to the file
    data.to_csv(
        file_path,
        mode='a',          # Append to the file we just created with the header
        header=False,      # Don't write DataFrame headers again
        index=False,       # Don't write the DataFrame index
        sep='\t',          # Use tabs as separators
        float_format='%.6f'# Format floats to 6 decimal places
    )

def load_sto_header(file_path):
    """
    Loads the header of a .sto file and returns it as a list of strings.

    Args:
        file_path (str): The path to the .sto file.

    Returns:
        list: A list of strings representing the header lines.
    """
    header = []
    break_next = False
    with open(file_path, 'r') as f:
        for line in f:
            if break_next:
                break
            if 'endheader' in line:
                break_next = True
            header.append(line.strip())
    
    return header

def write_sto_file(data, file_path, header):
    """
    Writes a pandas DataFrame to a .sto file with a specified header.

    Args:
        data (pd.DataFrame): The DataFrame to write.
        file_path (str): The path where the .sto file will be saved.
        header (list): A list of strings representing the header lines to write.
    """
    with open(file_path, 'w', newline='') as f:
        for line in header:
            f.write(line + '\n')
        
        # Write the data without extra line spaces
        data.to_csv(f, sep='\t', index=False, float_format='%.6f')

def read_xml(path):
    """
    Reads an XML file and returns its content as a string.

    Args:
        path (str): The path to the XML file.

    Returns:
        str: The content of the XML file.
    """
    try:
        tree = ET.parse(path)
        return tree
    except FileNotFoundError:
        print(f"Error: The file at {path} does not exist.")
        return None
    except Exception as e:
        print(f"Error reading the file at {path}: {e}")
        return None

def save_pretty_xml(tree, save_path):
            """Saves the XML tree to a file with proper indentation and no blank lines."""
            rough_string = ET.tostring(tree.getroot(), 'utf-8')
            reparsed = xml.dom.minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="   ")
            # Remove blank lines
            pretty_xml_no_blanks = "\n".join([line for line in pretty_xml.splitlines() if line.strip()])
            with open(save_path, 'w') as file:
                file.write(pretty_xml_no_blanks)

# opensim 

def select_osim_file():
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        title="Select OpenSim Model File",
        filetypes=[("OpenSim Model Files", "*.osim")]
    )
    root.destroy()
    return file_path

def checkMuscleMomentArms(osim_modelPath, ik_output, leg = 'l', threshold = 0.005):
# Adapted from Willi Koller: https://github.com/WilliKoller/OpenSimMatlabBasic/blob/main/checkMuscleMomentArms.m
# Only checked if works for for the Rajagopal and Catelli models

    def get_model_coord(model, coord_name):
        try:
            index = model.getCoordinateSet().getIndex(coord_name)
            coord = model.updCoordinateSet().get(index)
        except:
            index = None
            coord = None
            print(f'Coordinate {coord_name} not found in model')
        
        return index, coord


    # raise Exception('This function is not yet working. Please use the Matlab version for now or fix line containing " time_discontinuity.append(time_vector[discontinuity_indices]) "')

    # Load motions and model
    motion = osim.Storage(ik_output)
    model = osim.Model(osim_modelPath)

    # Initialize system and state
    model.initSystem()
    state = model.initSystem()

    # coordinate names
    flexIndexL, flexCoordL = get_model_coord(model, 'hip_flexion_' + leg)
    rotIndexL, rotCoordL = get_model_coord(model, 'hip_rotation_' + leg)
    addIndexL, addCoordL = get_model_coord(model, 'hip_adduction_' + leg)
    flexIndexLknee, flexCoordLknee = get_model_coord(model, 'knee_angle_' + leg)
    flexIndexLank, flexCoordLank = get_model_coord(model, 'ankle_angle_' + leg)

    # get names of the hip muscles
    numMuscles = model.getMuscles().getSize()
    muscleIndices_hip = []
    muscleNames_hip = []
    for i in range(numMuscles):
        tmp_muscleName = str(model.getMuscles().get(i).getName())
        if ('add' in tmp_muscleName or 'gl' in tmp_muscleName or 'semi' in tmp_muscleName or 'bf' in tmp_muscleName or
                'grac' in tmp_muscleName or 'piri' in tmp_muscleName or 'sart' in tmp_muscleName or 'tfl' in tmp_muscleName or
                'iliacus' in tmp_muscleName or 'psoas' in tmp_muscleName or 'rect' in tmp_muscleName) and ('_' + leg in tmp_muscleName):
            muscleIndices_hip.append(i)
            muscleNames_hip.append(tmp_muscleName)

    flexMomentArms = np.zeros((motion.getSize(), len(muscleIndices_hip)))
    addMomentArms = np.zeros((motion.getSize(), len(muscleIndices_hip)))
    rotMomentArms = np.zeros((motion.getSize(), len(muscleIndices_hip)))

    # get names of the knee muscles
    numMuscles = model.getMuscles().getSize()
    muscleIndices_knee = []
    muscleNames_knee = []
    for i in range(numMuscles):
        tmp_muscleName = str(model.getMuscles().get(i).getName())
        if ('bf' in tmp_muscleName or 'gas' in tmp_muscleName or 'grac' in tmp_muscleName or 'sart' in tmp_muscleName or
                'semim' in tmp_muscleName or 'semit' in tmp_muscleName or 'rec' in tmp_muscleName or 'vas' in tmp_muscleName) and ('_' + leg in tmp_muscleName):
            muscleIndices_knee.append(i)
            muscleNames_knee.append(tmp_muscleName)

    kneeFlexMomentArms = np.zeros((motion.getSize(), len(muscleIndices_knee)))

    # get names of the ankle muscles
    numMuscles = model.getMuscles().getSize()
    muscleIndices_ankle = []
    muscleNames_ankle = []
    for i in range(numMuscles):
        tmp_muscleName = str(model.getMuscles().get(i).getName())
        print(tmp_muscleName)
        if ('edl' in tmp_muscleName or 'ehl' in tmp_muscleName or 'tibant' in tmp_muscleName or 'gas' in tmp_muscleName or
                'fdl' in tmp_muscleName or 'fhl' in tmp_muscleName or 'perb' in tmp_muscleName or 'perl' in tmp_muscleName or
                'sole' in tmp_muscleName or 'tibpos' in tmp_muscleName) and ('_' + leg in tmp_muscleName):
            muscleIndices_ankle.append(i)
            muscleNames_ankle.append(tmp_muscleName)

    ankleFlexMomentArms = np.zeros((motion.getSize(), len(muscleIndices_ankle)))

    # compute moment arms for each muscle and create time vector
    time_vector = []
    for i in range(1, motion.getSize()):
        flexAngleL = motion.getStateVector(i-1).getData().get(flexIndexL) / 180 * np.pi
        rotAngleL = motion.getStateVector(i-1).getData().get(rotIndexL) / 180 * np.pi
        addAngleL = motion.getStateVector(i-1).getData().get(addIndexL) / 180 * np.pi
        flexAngleLknee = motion.getStateVector(i-1).getData().get(flexIndexLknee) / 180 * np.pi
        flexAngleLank = motion.getStateVector(i-1).getData().get(flexIndexLank) / 180 * np.pi

        time_vector.append(motion.getStateVector(i-1).getTime())
        # Update the state with the joint angle
        coordSet = model.updCoordinateSet()
        coordSet.get(flexIndexL).setValue(state, flexAngleL)
        coordSet.get(rotIndexL).setValue(state, rotAngleL)
        coordSet.get(addIndexL).setValue(state, addAngleL)
        coordSet.get(flexIndexLknee).setValue(state, flexAngleLknee)
        coordSet.get(flexIndexLank).setValue(state, flexAngleLank)

        # Realize the state to compute dependent quantities
        model.computeStateVariableDerivatives(state)
        model.realizeVelocity(state)

        # Compute the moment arm hip
        for j in range(len(muscleIndices_hip)):
            muscleIndex = muscleIndices_hip[j]
            if muscleNames_hip[j][-1] == leg:
                flexMomentArm = model.getMuscles().get(muscleIndex).computeMomentArm(state, flexCoordL)
                flexMomentArms[i, j] = flexMomentArm

                rotMomentArm = model.getMuscles().get(muscleIndex).computeMomentArm(state, rotCoordL)
                rotMomentArms[i, j] = rotMomentArm

                addMomentArm = model.getMuscles().get(muscleIndex).computeMomentArm(state, addCoordL)
                addMomentArms[i, j] = addMomentArm

        # Compute the moment arm knee
        for j in range(len(muscleNames_knee)):
            muscleIndex = muscleIndices_knee[j]
            if muscleNames_knee[j][-1] == leg:
                kneeFlexMomentArm = model.getMuscles().get(muscleIndex).computeMomentArm(state, flexCoordLknee)
                kneeFlexMomentArms[i, j] = kneeFlexMomentArm

        # Compute the moment arm ankle
        for j in range(len(muscleNames_ankle)):
            muscleIndex = muscleIndices_ankle[j]
            if muscleNames_ankle[j][-1] == leg:
                ankleFlexMomentArm = model.getMuscles().get(muscleIndex).computeMomentArm(state, flexCoordLank)
                ankleFlexMomentArms[i, j] = ankleFlexMomentArm

    # check discontinuities
    discontinuity = []
    muscle_action = []
    time_discontinuity = []

    fDistC = plt.figure('Discontinuity', figsize=(8, 8))
    plt.title(ik_output)

    save_folder = os.path.join(os.path.dirname(ik_output),'momentArmsCheck')

    def find_discontinuities(momArms, threshold, muscleNames, action, discontinuity, muscle_action, time_discontinuity):
        for i in range(momArms.shape[1]):
            dy = np.diff(momArms[:, i])
            discontinuity_indices = np.where(np.abs(dy) > threshold)[0]
            if discontinuity_indices.size > 0:
                print('Discontinuity detected at', muscleNames[i], 'at ', action, ' moment arm')
                plt.plot(momArms[:, i])
                plt.plot(discontinuity_indices, momArms[discontinuity_indices, i], 'rx')
                discontinuity.append(i)
                muscle_action.append(str(muscleNames[i] + ' ' + action + ' at frames: ' + str(discontinuity_indices)))
                time_discontinuity.append([time_vector[index] for index in discontinuity_indices])


        return discontinuity, muscle_action, time_discontinuity

    # hip flexion
    discontinuity, muscle_action, time_discontinuity = find_discontinuities(
        flexMomentArms, threshold, muscleNames_hip, 'flexion', discontinuity, muscle_action, time_discontinuity)

    # hip adduction
    discontinuity, muscle_action, time_discontinuity = find_discontinuities(
        addMomentArms, threshold, muscleNames_hip, 'adduction', discontinuity, muscle_action, time_discontinuity)
    
    # hip rotation
    discontinuity, muscle_action, time_discontinuity = find_discontinuities(
        rotMomentArms, threshold, muscleNames_hip, 'rotation', discontinuity, muscle_action, time_discontinuity)
    
    # knee flexion
    discontinuity, muscle_action, time_discontinuity = find_discontinuities(
        kneeFlexMomentArms, threshold, muscleNames_knee, 'flexion', discontinuity, muscle_action, time_discontinuity)
    
    # ankle flexion
    discontinuity, muscle_action, time_discontinuity = find_discontinuities(
        ankleFlexMomentArms, threshold, muscleNames_ankle, 'dorsiflexion', discontinuity, muscle_action, time_discontinuity)
    
    # plot discontinuities
    if len(discontinuity) > 0:
        plt.legend(muscle_action)
        plt.ylabel('Muscle Moment Arms with discontinuities (m)')
        plt.xlabel('Frame (after start time)')
        save_fig(plt.gcf(), save_path=os.path.join(save_folder, 'discontinuities_' + leg + '.png'))
        print('\n\nYou should alter the model - most probably you have to reduce the radius of corresponding wrap objects for the identified muscles\n\n\n')

        # save txt file with discontinuities
        with open(os.path.join(save_folder, 'discontinuities_' + leg + '.txt'), 'w') as f:
            f.write(f"model file = {osim_modelPath}\n")
            f.write(f"motion file = {ik_output}\n")
            f.write(f"leg checked = {leg}\n")
            
            f.write("\n muscles with discontinuities \n", ) 
            
            for i in range(len(muscle_action)):
                try:
                    f.write("%s : time %s \n" % (muscle_action[i], time_discontinuity[i]))
                except:
                    print('no discontinuities detected')

        momentArmsAreWrong = 1
    else:
        plt.close(fDistC)
        print('No discontinuities detected')
        momentArmsAreWrong = 0

    # plot hip flexion
    plt.figure('flexMomentArms_' + leg, figsize=(8, 8))
    plt.plot(flexMomentArms)
    plt.title('All muscle moment arms in motion ' + ik_output)
    plt.legend(muscleNames_hip, loc='best')
    plt.ylabel('Hip Flexion Moment Arm (m)')
    plt.xlabel('Frame (after start time)')
    save_fig(plt.gcf(), save_path=os.path.join(save_folder, 'hip_flex_MomentArms_' + leg + '.png'))

    # hip adduction
    plt.figure('addMomentArms_' + leg, figsize=(8, 8))
    plt.plot(addMomentArms)
    plt.title('All muscle moment arms in motion ' + ik_output)
    plt.legend(muscleNames_hip, loc='best')
    plt.ylabel('Hip Adduction Moment Arm (m)')
    plt.xlabel('Frame (after start time)')
    save_fig(plt.gcf(), save_path=os.path.join(save_folder, 'hip_add_MomentArms_' + leg + '.png'))

    # hip rotation
    plt.figure('rotMomentArms_' + leg, figsize=(8, 8))
    plt.plot(rotMomentArms)
    plt.title('All muscle moment arms in motion ' + ik_output)
    plt.legend(muscleNames_hip, loc='best')
    plt.ylabel('Hip Rotation Moment Arm (m)')
    plt.xlabel('Frame (after start time)')
    save_fig(plt.gcf(), save_path=os.path.join(save_folder, 'hip_rot_MomentArms_' + leg + '.png'))

    # knee flexion
    plt.figure('kneeFlexMomentArms_' + leg, figsize=(8, 8))
    plt.plot(kneeFlexMomentArms)
    plt.title('All muscle moment arms in motion ' + ik_output)
    plt.legend(muscleNames_knee, loc='best')
    plt.ylabel('Knee Flexion Moment Arm (m)')
    plt.xlabel('Frame (after start time)')
    save_fig(plt.gcf(), save_path=os.path.join(save_folder, 'knee_MomentArms_' + leg + '.png'))

    # ankle flexion
    plt.figure('ankleFlexMomentArms_' + leg, figsize=(8, 8))
    plt.plot(ankleFlexMomentArms)
    plt.title('All muscle moment arms in motion ' + ik_output)
    plt.legend(muscleNames_ankle, loc='best')
    plt.ylabel('Ankle Dorsiflexion Moment Arm (m)')
    plt.xlabel('Frame (after start time)')
    save_fig(plt.gcf(), save_path=os.path.join(save_folder, 'ankle_MomentArms_' + leg + '.png'))

    print('Moment arms checked for ' + ik_output)
    print('Results saved in ' + save_folder + ' \n\n' )

    return momentArmsAreWrong,  discontinuity, muscle_action


# User selects a factor to increase the max isometric force of muscles
def get_factor():
    root = tk.Tk()
    root.withdraw()
    factor = simpledialog.askfloat(
        "Increase Factor",
        "Enter factor to multiply max isometric force (e.g., 1.2):",
        minvalue=0.0
    )
    root.destroy()
    return factor

def increase_muscle_force(osim_file=None, factor=None, save_path=None):
    root = tk.Tk() # prevent the main window from appearing
    root.withdraw()
    if osim_file is None:
        osim_file = select_osim_file()
        
    if not osim_file:
        messagebox.showinfo("Cancelled", "No file selected.")
        return
    
    if factor is None:
        factor = get_factor()
        
    if not factor:
        messagebox.showinfo("Cancelled", "No factor entered.")
        return

    model = osim.Model(osim_file)
    muscles = model.getMuscles()
    for i in range(muscles.getSize()):
        muscle = muscles.get(i)
        orig_force = muscle.getMaxIsometricForce()
        muscle.setMaxIsometricForce(orig_force * factor)

    if save_path is None:
        new_file = osim_file.replace('.osim', f'_increased_{factor:.2f}.osim')
    else:
        new_file = save_path
        
    model.printToXML(new_file)
    messagebox.showinfo("Done", f"Saved new model to:\n{new_file}")



# plotting

def save_fig(fig, save_path):
    """Saves the figure to the specified path."""
    if not os.path.exists(os.path.dirname(save_path)):
        os.makedirs(os.path.dirname(save_path))
    fig.savefig(save_path, bbox_inches='tight')
    print(f"Figure saved to {save_path}")

def get_screen_size():

    try:
        import tkinter as tk
        root = tk.Tk()
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return width, height
    except Exception as e:
        print(f"Error getting screen size: {e}")
        return None

def calculate_nRows_nCold(n_subplots):
    """
    Calculate the number of rows and columns for subplots based on the number of subplots.

    Args:
        n_subplots (int): The total number of subplots.

    Returns:
        tuple: (nrows, ncols) where nrows is the number of rows and ncols is the number of columns.
    """
    import numpy as np
    # Find the smallest nrows and ncols such that nrows * ncols >= n_subplots and (nrows-1) * ncols < n_subplots
    ncols = int(np.ceil(np.sqrt(n_subplots)))
    nrows = int(np.ceil(n_subplots / ncols))
    while (nrows - 1) * ncols >= n_subplots:
        nrows -= 1
    return nrows, ncols

# data manipulation
def time_normalise_df(df, fs=''):

    if not type(df) == pd.core.frame.DataFrame:
        raise Exception('Input must be a pandas DataFrame')
    
    if not fs:
        try:
            fs = 1/(df['time'][1]-df['time'][0])
        except  KeyError as e:
            raise Exception('Input DataFrame must contain a column named "time"')
    
    normalised_df = pd.DataFrame(columns=df.columns)

    for column in df.columns:
        normalised_df[column] = np.zeros(101)

        currentData = df[column]
        currentData = currentData[~np.isnan(currentData)]
        
        timeTrial = np.arange(0, len(currentData)/fs, 1/fs)        
        Tnorm = np.arange(0, timeTrial[-1], timeTrial[-1]/101)
        if len(Tnorm) == 102:
            Tnorm = Tnorm[:-1]
        normalised_df[column] = np.interp(Tnorm, timeTrial, currentData)
    
    return normalised_df




if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Use arguments from the command line
        command = sys.argv[1]

        if command == "hello":
            print("hello")

        elif command == "load_trc":
            if len(sys.argv) > 2:
                path = sys.argv[2]
                data = load_trc(path, output=1)
            else:
                print("Please provide the path to the .trc file. Example: python utils.py load_trc path/to/file.trc")
        
        # run the command string as each function if it exists
        elif command == "load_mot":
            if len(sys.argv) > 2:
                path = sys.argv[2]
                data = load_mot(path, output=1)
            else:
                print("Please provide the path to the .mot file. Example: python utils.py load_mot path/to/file.mot")
        elif command == "load_sto":
            if len(sys.argv) > 2:
                path = sys.argv[2]
                data = load_sto(path, output=1)
            else:
                print("Please provide the path to the .sto file. Example: python utils.py load_sto path/to/file.sto")
        elif command == "load_c3d":
            if len(sys.argv) > 2:
                path = sys.argv[2]
                data = load_c3d(path, output=1)
            else:
                print("Please provide the path to the .c3d file. Example: python utils.py load_c3d path/to/file.c3d")
        elif command == "load_data_file":
            if len(sys.argv) > 2:
                path = sys.argv[2]
                data, metadata = load_data_file(path)
                print("Data loaded successfully.")
                print("Metadata:", metadata)
            else:
                print("Please provide the path to the data file. Example: python utils.py load_data_file path/to/file.txt")
                
        elif command == "save_data_file":
            if len(sys.argv) > 3:
                path = sys.argv[2]
                data = pd.read_csv(sys.argv[3], sep='\t')
                    
        elif command == "get_screen_size":
            screen_size = get_screen_size()
            if screen_size:
                print(f"Screen size: {screen_size[0]}x{screen_size[1]}")
            else:
                print("Could not determine screen size.")      
        
        elif command == "calculate_nRows_nCols":
            if len(sys.argv) > 2:
                n_subplots = int(sys.argv[2])
                nrows, ncols = calculate_nRows_nCold(n_subplots)
                print(f"Calculated rows: {nrows}, columns: {ncols} for {n_subplots} subplots.")
            else:
                print("Please provide the number of subplots. Example: python utils.py calculate_nRows_nCols 9")

        else:
            print(f"Unknown command: {command}")
# END