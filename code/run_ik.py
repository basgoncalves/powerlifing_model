import os
import shutil
import time
import opensim as osim
import utils
import settings
import xml.etree.ElementTree as ET


def validate_markers_used(osim_modelPath, ikTool, markers_path):
    
    model =  osim.Model(osim_modelPath)
    markerSet = model.get_MarkerSet() 
    markers_model = [marker.getName() for marker in markerSet]

    task_set_template = ikTool.get_IKTaskSet()
    markers_df = utils.load_trc(markers_path)
    markers_trc = markers_df.columns.get_level_values(0).unique().tolist()
    
    for marker_name in markers_model:
        if marker_name not in markers_df.columns:
            print(f"Warning: Marker '{marker_name}' not found in TRC file.")
            time.sleep(0.05)

    markers_in_task = [task.getName() for task in task_set_template if isinstance(task, osim.IKMarkerTask)]

    for marker_name in markers_model:
        if marker_name in markers_in_task:
            if marker_name in markers_trc:
                task = task_set_template.get(marker_name)
                task.setApply(True)
                breakpoint()
            else:
                task = task_set_template.get(marker_name)
                task.setApply(False)
                print(f"Marker '{marker_name}' not found in TRC file. Disabling task.")
        else:
            newTask = osim.IKMarkerTask()
            newTask.setName(marker_name)
            newTask.setWeight(1.0)
            if marker_name in markers_trc:
                newTask.setApply(True)
                print(f"Marker '{marker_name}' found in TRC file. Adding and applying with weight 1.0.")
            else:
                newTask.setApply(False)
                print(f"Marker '{marker_name}' in Model not found in TRC file. Disabling task.")
                
            ikTool.get_IKTaskSet().adoptAndAppend(newTask)

    
    return ikTool

def main(osim_modelPath=None, marker_trc=None, ik_output=None, setup_xml=None, time_range=None, resultsDir=None):
    
    if osim_modelPath is None:
        osim_modelPath = input("Enter the path to the OpenSim model file (.osim): ").strip('"')
    if marker_trc is None:
        marker_trc = input("Enter the path to the marker TRC file (.trc): ").strip('"')
    if ik_output is None:
        ik_output = input("Enter the desired output path for the IK results (.mot): ").strip('"')
    if setup_xml is None:
        setup_xml = input("Enter the path to save the IK setup XML file (.xml): ").strip('"')
    if resultsDir is None:
        resultsDir = os.path.dirname(ik_output)
        
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
        
    if not os.path.exists(osim_modelPath):
        utils.print_to_log(f"OpenSim model file not found: {osim_modelPath}")
    
    if not os.path.exists(marker_trc):
        utils.print_to_log(f"Marker TRC file not found: {marker_trc}")

    if not os.path.exists(resultsDir):
        os.makedirs(resultsDir, exist_ok=True)
    
    os.chdir(resultsDir)
    
    # Load the model
    print(f"Loading OpenSim model from {osim_modelPath}")
    model = osim.Model(osim_modelPath)
    model.initSystem()
    
    # Load markers
    markers = osim.Storage(marker_trc)

    # Create the Inverse Kinematics tool
    ikTool = osim.InverseKinematicsTool(setup_xml)
    
    # simple function to validate the markers used in the IK setup
    ikTool = validate_markers_used(osim_modelPath, ikTool, marker_trc)
    
    # Set the model and parameters
    ikTool.setModel(model)
    # Set the marker data file and time range
    ikTool.setMarkerDataFileName(marker_trc)
    ikTool.set_report_marker_locations(True)
    ikTool.set_report_errors(True)
    
    # set the time range for the IK calculation
    if time_range is not None:
        
        # check time range is valid
        if time_range[0] < markers.getFirstTime() or time_range[1] > markers.getLastTime():
            print("Warning: Specified time range is outside the bounds of the marker data. Using full range instead.")
            time_range = [markers.getFirstTime(), markers.getLastTime()]
        
        ikTool.setStartTime(time_range[0])  # Set start time
        ikTool.setEndTime(time_range[1])    # Set end time
    else:
        ikTool.setStartTime(markers.getFirstTime())  # Default start time
        ikTool.setEndTime(markers.getLastTime())    # Default end time
    
    # Set the output motion file name relative to the results directory
    ikTool.setResultsDir('./')
    ikTool.setOutputMotionFileName(os.path.relpath(ik_output, resultsDir))
    ikTool.printToXML(setup_xml)
    print(f"Inverse Kinematics setup saved to {os.path.abspath(setup_xml)}")
    time.sleep(1)  # Optional: wait for a second before running the tool
    
    # Reload tool from xml
    ikTool = osim.InverseKinematicsTool(setup_xml)
    ikTool.setModel(model)
    
    # Run the inverse kinematics calculation
    ikTool.run()
    
    print(f"Inverse Kinematics calculation completed. Results saved to {resultsDir}")

def optimise_ik_weights(osim_modelPath, setup_xml):
    """
    Function to optimise IK marker weights based on marker errors.
    """
    
    
    

if __name__ == '__main__':
    
    main()
        

    
    
  