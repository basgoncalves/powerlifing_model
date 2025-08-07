import os
import shutil
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
            task.setWeight(task.getWeight())
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
    base_dir = paths.SIMULATION_DIR
    subject = 'Athlete_03'  # Replace with actual subject name
    session = '22_07_06'  # Replace with actual session name
    trial = 'dl_85'  # Replace with actual trial name
    
    # create a trial instance
    trial = paths.Trial(subject_name=subject, session_name=session, trial_name=trial)

    setup_xml = os.path.join(trial.path, trial.outputFiles['IK'].setup)
    if not os.path.exists(setup_xml):
        shutil.copyfile(src= os.path.join(paths.SETUP_DIR, trial.outputFiles['IK'].setup), 
                        dst=setup_xml)

    # copy setup 
    osim_modelPath = trial.USED_MODEL
    ik_mot = trial.outputFiles['IK'].abspath()
    setup_id = trial.path + '\\' + trial.outputFiles['IK'].setup
    grf_xml = trial.inputFiles['GRF_XML'].abspath()
    
    main(osim_modelPath=osim_modelPath,
            marker_trc=trial.inputFiles['MARKERS'].abspath(),
            ik_output=ik_mot,
            setup_xml=setup_id,
            time_range=trial.TIME_RANGE,
            resultsDir=trial.path)
    
    
  