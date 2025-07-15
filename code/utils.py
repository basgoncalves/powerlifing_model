import pandas as pd
import sys
import pandas as pd
import re
import c3d
import xml.etree.ElementTree as ET
import xml.dom.minidom
import os

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
        sys.exit(1)
        
    # read headers in line i
    try:
        with open(path, 'r') as file:
            headers = file.readlines()[i].strip().split('\t')
    except:
        print(f"Error: Could not read the file at {path}. Please check the path and try again.")
        sys.exit(1)

    # read the file into a pandas DataFrame, skipping the header
    try:
        data = pd.read_csv(path, sep= '\s+', header=i+1, index_col=False)
        # add the headers to the DataFrame above the data
        data.columns = headers
        
    except Exception as e:
        print(f"Error: Could not read the file at {path}. Please check the file format and try again.")
        print(f"Details: {e}")
        sys.exit(1)

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
        sys.exit(1)
    
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
        sys.exit(1)

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
        sys.exit(1)

    # read the file into a pandas DataFrame, skipping the header
    try:
        data = pd.read_csv(path, sep= '\s+', header=i+1)
    except Exception as e:
        print(f"Error: Could not read the file at {path}. Please check the file format and try again.")
        print(f"Details: {e}")
        sys.exit(1)

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
        sys.exit(1)

    # read the file into a pandas DataFrame, skipping the header
    try:
        data = pd.read_csv(path, sep= '\s+', header=i+1)
    except Exception as e:
        print(f"Error: Could not read the file at {path}. Please check the file format and try again.")
        print(f"Details: {e}")
        sys.exit(1)

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
        raise ValueError(f"Unsupported file format: {file_path}")

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


# plotting
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