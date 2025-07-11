import os
import opensim as osim
import paths
import utils

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
    
    # check the markers
    task_set = ikTool.get_IKTaskSet()
    markers = utils.load_trc(paths.MARKERS_TRC)
    print(markers)
    
    markers_list = [col for col in markers.columns if col.strip()]
    
    for task in task_set:
        if task.getName() in markers_list:
            task.setApply(True)
            task.setWeight(1.0)
        else:
            task.setApply(False)
        print(f"Task: {task.getName()}, Apply: {task.getApply()}, Weight: {task.getWeight()}")
    
    
    ikTool.setModel(model)
    ikTool.setMarkerDataFileName(str(marker_trc))
    ikTool.setStartTime(time_range[0])  # Set start time
    ikTool.setEndTime(time_range[1])    # Set end time
    ikTool.setResultsDir(resultsDir)
    ikTool.setOutputMotionFileName(ik_output)
    ikTool.printToXML(setup_xml)
    print(f"Inverse Kinematics setup saved to {setup_xml}")

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
    
    # get time range from the marker file if not provided
    events = utils.pd.read_csv(paths.EVENTS, index_col=0, header=None)
    time_range = [events.iloc[0,0], events.iloc[1,0]]
    print(f'Time range for IK: {time_range}')

    print(f'osim version: {osim.__version__}')
    run_IK(osim_modelPath, marker_trc,ik_output, setup_ik, time_range=time_range)
  