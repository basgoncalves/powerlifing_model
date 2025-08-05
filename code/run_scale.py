import os
import shutil
import time
import opensim as osim
import paths
import utils

def validate_markers_used(scaleTool, markers_path):
    # For scaling, you might validate marker set differently or skip this
    markers = utils.load_trc(markers_path)
    markers_list = [col for col in markers.columns if col.strip()]
    print(f"Markers available for scaling: {markers_list}")
    return scaleTool

def main(generic_osim_model_path, marker_trc, scale_output, setup_xml, resultsDir=None):

    os.chdir(resultsDir)
    if not os.path.exists(resultsDir):
        os.makedirs(resultsDir)

    if not os.path.exists(generic_osim_model_path):
        utils.print_to_log(f"OpenSim model file not found: {generic_osim_model_path}")

    if not os.path.exists(marker_trc):
        utils.print_to_log(f"Marker TRC file not found: {marker_trc}")

    # Load the model
    print(f"Loading OpenSim model from {generic_osim_model_path}")
    model = osim.Model(generic_osim_model_path)
    model.initSystem()

    # Create the Scale tool
    scaleTool = osim.ScaleTool(setup_xml)

    # Optionally validate markers used in the scaling setup
    scaleTool = validate_markers_used(scaleTool, marker_trc)

    # Set the model and parameters
    scaleTool.setSubjectMass(model.getTotalMass())
    scaleTool.setSubjectHeight(1.75)  # Example, set as needed

    # Set the marker data file and time range
    scaleTool.setMarkerFileName(marker_trc)

    # set the time range for the scaling calculation
    if time_range is not None:
        scaleTool.setTimeRange(osim.ArrayDouble(time_range, 2))

    # Set the output scaled model file name relative to the results directory
    scaleTool.setOutputModelFileName(scale_output)
    scaleTool.printToXML(setup_xml)
    print(f"Scale setup saved to {setup_xml}")
    time.sleep(1)  # Optional: wait for a second before running the tool

    # Reload tool from xml
    scaleTool = osim.ScaleTool(setup_xml)

    # Run the scaling calculation
    scaleTool.run()

    print(f"Scaling completed. Results saved to {resultsDir}")

if __name__ == '__main__':
    base_dir = paths.SIMULATION_DIR
    subject = 'Athlete_03'  # Replace with actual subject name
    session = '22_07_06'  # Replace with actual session name
    trial = 'dl_85'  # Replace with actual trial name

    # create a trial instance
    trial = paths.Trial(subject_name=subject, session_name=session, trial_name=trial)

    setup_xml = os.path.join(trial.path, trial.outputFiles['SCALE'].setup)
    if not os.path.exists(setup_xml):
        shutil.copyfile(src=os.path.join(paths.SETUP_DIR, trial.outputFiles['SCALE'].setup),
                        dst=setup_xml)

    osim_modelPath = trial.USED_MODEL
    scale_model = trial.outputFiles['SCALE'].abspath()
    setup_id = trial.path + '\\' + trial.outputFiles['SCALE'].setup

    main(generic_osim_model_path=osim_modelPath,
         marker_trc=trial.inputFiles['MARKERS'].abspath(),
         scale_output=scale_model,
         setup_xml=setup_id,
         time_range=trial.TIME_RANGE,
         resultsDir=trial.path)
