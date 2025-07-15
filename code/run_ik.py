import os
import time
import opensim as osim
import paths
import utils

def validate_markers_used(ikTool):
    task_set = ikTool.get_IKTaskSet()
    markers = utils.load_trc(paths.MARKERS_TRC)
    
    markers_list = [col for col in markers.columns if col.strip()]
    
    for task in task_set:
        if task.getName() in markers_list:
            task.setApply(True)
            task.setWeight(1.0)
        else:
            task.setApply(False)
        print(f"Task: {task.getName()}, Apply: {task.getApply()}, Weight: {task.getWeight()}")
    
    return ikTool

def run_IK(osim_modelPath, marker_trc, ik_output, setup_xml, time_range=None):
    
    resultsDir = os.path.dirname(setup_xml)
    if not os.path.exists(resultsDir):
        os.makedirs(resultsDir)

    if not os.path.exists(osim_modelPath):
        raise FileNotFoundError(f"OpenSim model file not found: {osim_modelPath}")
    
    if not os.path.exists(marker_trc):
        
        raise FileNotFoundError(f"Marker TRC file not found: {marker_trc}")

    # Load the model
    print(f"Loading OpenSim model from {osim_modelPath}")
    model = osim.Model(osim_modelPath)
    model.initSystem()

    # Create the Inverse Kinematics tool
    ikTool = osim.InverseKinematicsTool(paths.GENERIC_SETUP_IK)
    
    # simple function to validate the markers used in the IK setup
    ikTool = validate_markers_used(ikTool)
    
    # Set the model and parameters
    ikTool.setModel(model)
    # Set the marker data file and time range
    ikTool.setMarkerDataFileName(os.path.relpath(marker_trc, start=os.path.dirname(setup_xml)))
    ikTool.setStartTime(time_range[0])  # Set start time
    ikTool.setEndTime(time_range[1])    # Set end time
    
    # Set the output motion file name relative to the results directory
    ikTool.setResultsDir(os.path.relpath(resultsDir, start=os.path.dirname(setup_xml)))
    ikTool.setOutputMotionFileName(os.path.relpath(ik_output, start=os.path.dirname(setup_xml)))
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
        run_IK(osim_modelPath, marker_trc,ik_output, setup_ik, time_range=paths.TIME_RANGE)
    except Exception as e:
        print(f"Error running Inverse Kinematics: {e}")
        exit(1)
    
    
  