import shutil
import opensim as osim
import paths
import utils
import os

def create_analysis_tool(coordinates_file, externalloadsfile, model_path, results_directory, actuators=None):
    """Creates and configures an OpenSim AnalyzeTool object.

    Args:
    coordinates_file: Path to the motion data file (e.g., .trc or .mot).
    model_path: Path to the OpenSim model file (.osim).
    results_directory: Path to the directory for storing results.
    force_set_files (optional): List of paths to actuator force set files.

    Returns:
    OpenSim AnalyzeTool object.

    # Example usage:
        coordinates_file = "your_motion_data.trc"
        model_path = "your_model.osim"
        results_directory = "analysis_results"
        force_set_files = ["actuator1_forces.xml", "actuator2_forces.xml"]  # Optional

        analysis_tool = create_analysis_tool(coordinates_file, model_path, results_directory, force_set_files)

        # Run the analysis
        analysis_tool.run()
    """

    # Load the motion data
    mot_data = osim.Storage(coordinates_file)

    # Get initial and final time
    initial_time = mot_data.getFirstTime()
    final_time = mot_data.getLastTime()

    # Create and set model
    model = osim.Model(model_path)
    analyze_tool = osim.AnalyzeTool()
    analyze_tool.setModel(model)

    # Set other parameters
    relpath_modelfile = os.path.relpath(model_path, start=os.path.dirname(coordinates_file))
    analyze_tool.setModelFilename(relpath_modelfile)
    analyze_tool.setReplaceForceSet(False)
    
    # set results directory
    relpath_results_directory = os.path.relpath(results_directory, start=os.path.dirname(coordinates_file))
    analyze_tool.setResultsDir(relpath_results_directory)
    analyze_tool.setOutputPrecision(8)

    # Set actuator force files (if provided)
    if actuators:
        force_set = osim.ArrayStr()
        for file in actuators:
            force_set.append(file)
        analyze_tool.setForceSetFiles(force_set)

    # Set initial and final time
    analyze_tool.setInitialTime(initial_time)
    analyze_tool.setFinalTime(final_time)

    # Set analysis parameters
    analyze_tool.setSolveForEquilibrium(False)
    analyze_tool.setMaximumNumberOfSteps(20000)
    analyze_tool.setMaxDT(1)
    analyze_tool.setMinDT(1e-8)
    analyze_tool.setErrorTolerance(1e-5)

    # Set external loads and coordinates files
    relpath_externalloadsfile = os.path.relpath(externalloadsfile, start=os.path.dirname(coordinates_file))
    relpath_coordinates_file = os.path.relpath(coordinates_file, start=os.path.dirname(coordinates_file))
    analyze_tool.setExternalLoadsFileName(relpath_externalloadsfile)  # Replace with your filename
    analyze_tool.setCoordinatesFileName(relpath_coordinates_file)

    # Set filter cutoff frequency
    analyze_tool.setLowpassCutoffFrequency(6)


    # Return the analysis tool
    return analyze_tool


def run_jra(modelpath, coordinates_file, externalloadsfile, setupJRA, actuators, muscle_forces, results_directory):
    # start model
    osimModel = osim.Model(modelpath)

    # Get mot data to determine time range
    motData = osim.Storage(coordinates_file)

    # Get initial and intial time
    initial_time = motData.getFirstTime()
    final_time = motData.getLastTime()
    
    # start joint reaction analysis
    jr = osim.JointReaction(setupJRA)
    jr.setName('JRA')
    # jr.setModel(osimModel)

    inFrame = osim.ArrayStr()
    onBody = osim.ArrayStr()
    jointNames = osim.ArrayStr()
    inFrame.set(0, 'child')
    onBody.set(0, 'child')
    jointNames.set(0, 'all')

    jr.setInFrame(inFrame)
    jr.setOnBody(onBody)
    jr.setJointNames(jointNames)

    # Set other parameters as needed
    jr.setStartTime(initial_time)
    jr.setEndTime(final_time)
    jr.setForcesFileName(os.path.relpath(muscle_forces, start=os.path.dirname(setupJRA)))

    # add to analysis tool
    analyzeTool_JR = create_analysis_tool(coordinates_file = coordinates_file,
                                          externalloadsfile = externalloadsfile,
                                          model_path = modelpath, 
                                          results_directory = results_directory, 
                                          actuators=actuators)
    
    analyzeTool_JR.setName('Analyse')
    analyzeTool_JR.getAnalysisSet().cloneAndAppend(jr)
    osimModel.addAnalysis(jr)

    # save setup file and run
    os.chdir(os.path.dirname(setupJRA))
    analyzeTool_JR.printToXML(setupJRA)
    analyzeTool_JR = osim.AnalyzeTool(setupJRA)
    print('jra for', results_directory)
    analyzeTool_JR.run()
    
def run_jra_setup(modelpath, setupJRA):
    """Creates a Joint Reaction Analysis setup file."""
    if not os.path.exists(setupJRA):
        raise FileNotFoundError(f"Setup file not found: {setupJRA}")
    
    # Create the Joint Reaction Analysis tool
    jraTool = osim.AnalyzeTool(setupJRA)
    jraTool.setModel(osim.Model(modelpath))
    jraTool.setModelFilename(os.path.relpath(modelpath, start=os.path.dirname(setupJRA)))
    
    jraTool.printToXML(setupJRA)
    print(f"Joint Reaction Analysis setup saved to {setupJRA}")
    os.chdir(os.path.dirname(setupJRA))
    jraTool.run()
    print(f"Joint Reaction Analysis completed. Results saved to {os.path.dirname(setupJRA)}")
    
    
if __name__ == '__main__':
    modelpath = paths.USED_MODEL
    coordinates_file = paths.IK_OUTPUT
    muscle_forces = paths.FORCES_OUTPUT
    
    utils.print_to_log(f'Running JRA on: {paths.SUBJECT} / {paths.TRIAL_NAME} / {modelpath}')
    
    if not os.path.exists(modelpath):
        utils.print_to_log(f'OpenSim model file not found: {modelpath}')
        raise FileNotFoundError(f"OpenSim model file not found: {modelpath}")
    
    if not os.path.exists(coordinates_file):
        import run_ik
        run_ik.main(osim_modelPath=modelpath, marker_trc=paths.MARKERS_TRC, 
                      ik_output=coordinates_file, setup_xml=paths.SETUP_IK, time_range=paths.TIME_RANGE)
    
    if not os.path.exists(muscle_forces):
        import run_so
        
        run_so.main(osim_modelPath = modelpath, 
                      ik_output = coordinates_file, 
                      grf_xml = paths.GRF_XML,
                      resultsDir = paths.SO_OUTPUT, 
                      actuators = paths.ACTUATORS_SO)
    
    print(f'Running Joint Reaction Analysis on model: {modelpath}')
    try:
        if not os.path.exists(paths.SETUP_JRA):
            shutil.copy(paths.GENERIC_SETUP_JRA, paths.SETUP_JRA)
        
        run_jra(modelpath = modelpath, 
                coordinates_file = coordinates_file, 
                externalloadsfile = paths.GRF_XML,
                setupJRA = paths.SETUP_JRA,
                actuators = None,
                muscle_forces = muscle_forces, 
                results_directory = os.path.dirname(paths.JRA_OUTPUT))
        
        # run_jra_setup(modelpath=modelpath, 
        #                 setupJRA=paths.SETUP_JRA)
        
        print(f"Joint Reaction Analysis completed. Results saved to {paths.JRA_OUTPUT}")
        utils.print_to_log(f"Joint Reaction Analysis completed. Results saved to {paths.JRA_OUTPUT}")
    except Exception as e:
        print(f"Error during Joint Reaction Analysis: {e}")
        utils.print_to_log(f"Error during Joint Reaction Analysis: {e}")
        