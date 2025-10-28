import os
import shutil
import time
import opensim as osim
import utils
import settings

def validate_markers_used(ikTool,markers_path):
    task_set = ikTool.get_IKTaskSet()
    markers = utils.load_trc(markers_path)
    markers_list = markers.columns.get_level_values(0).unique().tolist()

    for task in task_set:
        if task.getName() in markers_list:
            task.setApply(True)
            task.setWeight(task.getWeight())
        else:
            task.setApply(False)
        print(f"Task: {task.getName()}, Apply: {task.getApply()}, Weight: {task.getWeight()}")
    
    return ikTool

def main(osim_modelPath=None, marker_trc=None, ik_output=None, setup_xml=None, time_range=None, resultsDir=None):
    
    if not os.path.exists(resultsDir):
        os.makedirs(resultsDir, exist_ok=True)
    
    os.chdir(resultsDir)
    
    if not os.path.exists(osim_modelPath):
        utils.print_to_log(f"OpenSim model file not found: {osim_modelPath}")
    
    if not os.path.exists(marker_trc):
        utils.print_to_log(f"Marker TRC file not found: {marker_trc}")

    # Load the model
    print(f"Loading OpenSim model from {osim_modelPath}")
    model = osim.Model(osim_modelPath)
    model.initSystem()
    
    # Load markers
    markers = osim.Storage(marker_trc)

    # Create the Inverse Kinematics tool
    ikTool = osim.InverseKinematicsTool(setup_xml)
    
    # simple function to validate the markers used in the IK setup
    ikTool = validate_markers_used(ikTool, marker_trc)
    
    # Set the model and parameters
    ikTool.setModel(model)
    # Set the marker data file and time range
    ikTool.setMarkerDataFileName(marker_trc)
    ikTool.set_report_marker_locations(True)
    ikTool.set_report_errors(True)
    
    # set the time range for the IK calculation
    if time_range is not None:
        ikTool.setStartTime(time_range[0])  # Set start time
        ikTool.setEndTime(time_range[1])    # Set end time
    else:
        ikTool.setStartTime(markers.getFirstTime())  # Default start time
        ikTool.setEndTime(markers.getLastTime())    # Default end time
    
    # Set the output motion file name relative to the results directory
    ikTool.setResultsDir('./')
    ikTool.setOutputMotionFileName(os.path.relpath(ik_output, resultsDir))
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
    
    # create a trial instance
    trial = utils.Trial(subject_name=settings.subject, 
                        session_name=settings.session, 
                        trial_name=settings.trial)
    
    setup_xml = os.path.join(trial.path, settings.SetupFiles().IK)
    
    if not os.path.exists(setup_xml):
        shutil.copyfile(src=os.path.join(settings.SETUP_DIR, settings.SetupFiles().IK), 
                        dst=setup_xml)

    # copy setup 
    osim_modelPath = str(trial.inputFiles.osimModel)
    ik_mot = str(trial.outputFiles.IK)
    setup_xml = str(trial.setupFiles.IK)
    markers = str(trial.inputFiles.MARKERS)
    time_range = trial.TIME_RANGE

    if settings.Execute().IK:
        main(osim_modelPath=osim_modelPath, 
             marker_trc=markers, 
             ik_output=ik_mot, 
             setup_xml=setup_xml, 
             time_range=time_range, 
             resultsDir=trial.path)
        

    
    
  