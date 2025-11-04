import os
import shutil
import time
import opensim as osim
import utils
import settings
import xml.etree.ElementTree as ET

def 


def main(osim_modelPath=None, marker_trc=None, time_range=None, outputFilePath=None):
    
    if osim_modelPath is None:
        osim_modelPath = input("Enter the path to the OpenSim model file (.osim): ").strip('"')
    if marker_trc is None:
        marker_trc = input("Enter the path to the marker TRC file (.trc): ").strip('"')
    if outputFilePath is None:
        outputFilePath = input("Enter the desired output path for the IK results (.mot): ").strip('"')

    if time_range is None:
        time_range_input = input("Enter the time range for IK calculation as 'start,end' (or press Enter to use full range): ").strip('"')
        if time_range_input:
            try:
                start_str, end_str = time_range_input.split(',')
                time_range = (float(start_str), float(end_str))
            except ValueError:
                print("Invalid time range format. Using full range.")
                time_range = None
        else:
            time_range = None
    
    if not os.path.exists(resultsDir):
        os.makedirs(resultsDir)
    
    # Load the model
    print(f"Loading OpenSim model from {osim_modelPath}")
    model = osim.Model(osim_modelPath)
    model.initSystem()
    
    # Load the marker data
    markers = osim.MarkerData(marker_trc)
    
    # Create the Inverse Kinematics tool