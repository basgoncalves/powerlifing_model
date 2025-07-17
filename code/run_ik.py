import os
import time
import opensim as osim
import paths
import utils

def validate_markers_used(ikTool,markers_path):
    task_set = ikTool.get_IKTaskSet()
    markers = utils.load_trc(markers_path)
    
    markers_list = [col for col in markers.columns if col.strip()]
    
    for task in task_set:
        if task.getName() in markers_list:
            task.setApply(True)
            task.setWeight(1.0)
        else:
            task.setApply(False)
        print(f"Task: {task.getName()}, Apply: {task.getApply()}, Weight: {task.getWeight()}")
    
    return ikTool

def main(osim_modelPath, marker_trc, ik_output, setup_xml, time_range=None, resultsDir=None):
    
    os.chdir(resultsDir)
    if not os.path.exists(resultsDir):
        os.makedirs(resultsDir)

    if not os.path.exists(osim_modelPath):
        utils.print_to_log(f"OpenSim model file not found: {osim_modelPath}")
    
    if not os.path.exists(marker_trc):
        utils.print_to_log(f"Marker TRC file not found: {marker_trc}")

    # Load the model
    print(f"Loading OpenSim model from {osim_modelPath}")
    model = osim.Model(osim_modelPath)
    model.initSystem()

    # Create the Inverse Kinematics tool
    ikTool = osim.InverseKinematicsTool(setup_xml)
    
    # simple function to validate the markers used in the IK setup
    ikTool = validate_markers_used(ikTool, marker_trc)
    
    # Set the model and parameters
    ikTool.setModel(model)
    # Set the marker data file and time range
    ikTool.setMarkerDataFileName(marker_trc)
    
    # set the time range for the IK calculation
    if time_range is not None:
        ikTool.setStartTime(time_range[0])  # Set start time
        ikTool.setEndTime(time_range[1])    # Set end time
    
    # Set the output motion file name relative to the results directory
    ikTool.setResultsDir('./')
    ikTool.setOutputMotionFileName(ik_output)
    ikTool.printToXML(setup_xml)
    print(f"Inverse Kinematics setup saved to {setup_xml}")
    time.sleep(1)  # Optional: wait for a second before running the tool
    
    # Reload tool from xml
    ikTool = osim.InverseKinematicsTool(setup_xml)
    ikTool.setModel(model)
    
    # Run the inverse kinematics calculation
    ikTool.run()
    
    print(f"Inverse Kinematics calculation completed. Results saved to {resultsDir}")

if __name__ == '__main__':
    osim_modelPath = paths.USED_MODEL
    marker_trc = paths.MARKERS_TRC
    setup_ik = paths.SETUP_IK
    ik_output = paths.IK_OUTPUT
    
    print(f'Time range for IK: {paths.TIME_RANGE}')

    print(f'osim version: {osim.__version__}')
    
    try:
        utils.print_to_log(f'{time.time}: Running Inverse Kinematics on model: {osim_modelPath}')
        main(osim_modelPath, marker_trc,ik_output, setup_ik, time_range=paths.TIME_RANGE)
    except Exception as e:
        print(f"Error running Inverse Kinematics: {e}")
        utils.print_to_log(f'{time.time}: Error running Inverse Kinematics: {e}')
        exit(1)
    
    utils.print_to_log(f'{time.time}: Inverse Kinematics run completed.')
    
    
  