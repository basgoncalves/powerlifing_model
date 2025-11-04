import shutil
import opensim as osim
import settings
import utils
import os

def create_analysis_tool(coordinates_file, externalloadsfile, model_path, 
                         results_directory, actuators=None):
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


def main(osim_modelPath=None, ik_output=None, 
         grf_xml=None, setup_xml=None, actuators=None, 
         muscle_force_path=None, resultsDir=None):
    
    if not osim_modelPath:
        osim_modelPath = input("Enter the path to the OpenSim model file (.osim): ").strip('"')
    if not ik_output:
        ik_output = input("Enter the path to the coordinates motion file (.mot or .trc): ").strip('"')
    if not grf_xml:
        grf_xml = input("Enter the path to the external loads file (.xml): ").strip('"')
    if not setup_xml:
        setup_xml = input("Enter the path to save the JRA setup XML file (.xml): ").strip('"')
    
    if not muscle_force_path:
        muscle_force_path = input("Enter the path to the muscle forces file (.sto): ").strip('"')
    
    if not resultsDir:
        resultsDir = os.path.dirname(ik_output)
    
    
    # start model
    osimModel = osim.Model(osim_modelPath)

    # Get mot data to determine time range
    motData = osim.Storage(ik_output)

    # Get initial and intial time
    initial_time = motData.getFirstTime()
    final_time = motData.getLastTime()
    
    # start joint reaction analysis
    jr = osim.JointReaction(setup_xml)
    jr.setName('JRA')
    
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
    jr.setForcesFileName(os.path.relpath(muscle_force_path, start=os.path.dirname(os.path.abspath(setup_xml)))) # Has to be absolute path

    # add to analysis tool
    analyzeTool_JR = create_analysis_tool(coordinates_file = ik_output,
                                          externalloadsfile = grf_xml,
                                          model_path = osim_modelPath, 
                                          results_directory = resultsDir, 
                                          actuators=actuators)
    
    analyzeTool_JR.setName('Analyse')
    analyzeTool_JR.getAnalysisSet().cloneAndAppend(jr)
    osimModel.addAnalysis(jr)

    # save setup file and run
    analyzeTool_JR.printToXML(setup_xml)
    analyzeTool_JR = osim.AnalyzeTool(setup_xml)
    print('jra for', resultsDir)
    analyzeTool_JR.run()
    
def run_jra_setup(osim_modelPath, setupJRA):
    """Creates a Joint Reaction Analysis setup file."""
    if not os.path.exists(setupJRA):
        raise FileNotFoundError(f"Setup file not found: {setupJRA}")
    
    # Create the Joint Reaction Analysis tool
    jraTool = osim.AnalyzeTool(setupJRA)
    jraTool.setModel(osim.Model(osim_modelPath))
    jraTool.setModelFilename(os.path.relpath(osim_modelPath, start=os.path.dirname(setupJRA)))
    
    jraTool.printToXML(setupJRA)
    print(f"Joint Reaction Analysis setup saved to {setupJRA}")
    os.chdir(os.path.dirname(setupJRA))
    jraTool.run()
    print(f"Joint Reaction Analysis completed. Results saved to {os.path.dirname(setupJRA)}")
    
    
if __name__ == '__main__':
   
    
    try:
        main()
    except Exception as e:
        utils.print_to_log(f'Error during Joint Reaction Analysis: {e}')
        exit()
