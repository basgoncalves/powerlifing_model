import os
import shutil
import opensim as osim
import paths
import utils
import time

def run_SO(osim_modelPath, ik_output, grf_xml, actuators, resultsDir):
    if not os.path.exists(resultsDir):
        os.makedirs(resultsDir)

    if not os.path.exists(osim_modelPath):
        raise FileNotFoundError(f"OpenSim model file not found: {osim_modelPath}")
    
    if not os.path.exists(ik_output):
        raise FileNotFoundError(f"Inverse Kinematics motion file not found: {ik_output}")
    
    if not os.path.exists(grf_xml):
        raise FileNotFoundError(f"Ground Reaction Forces XML file not found: {grf_xml}")
    
    # Load the model
    print(f"Loading OpenSim model from {osim_modelPath}")
    
    time.sleep(1)  # Optional: wait for a second before loading the model
    
    model = osim.Model(osim_modelPath)
    model.initSystem()
    
    # Create a StaticOptimization object
    so = osim.StaticOptimization()
    so.setStartTime(paths.TIME_RANGE[0])
    so.setEndTime(paths.TIME_RANGE[1])
    so.setInDegrees(True)
    so.setUseMusclePhysiology(True)
    so.setUseModelForceSet(True)
    
    # Create analyze tool for static optimization
    so_analyze_tool = osim.AnalyzeTool()
    so_analyze_tool.setName("SO")

    # Set model file, motion files and external load file names
    so_analyze_tool.setModelFilename(os.path.relpath(paths.USED_MODEL, start=os.path.dirname(paths.SETUP_SO)))
    so_analyze_tool.setCoordinatesFileName(os.path.relpath(ik_output, start=os.path.dirname(paths.SETUP_SO)))
    so_analyze_tool.setExternalLoadsFileName(os.path.relpath(paths.GRF_XML, start=os.path.dirname(paths.SETUP_SO)))
    so_analyze_tool.setReplaceForceSet(False)
    so_analyze_tool.getForceSetFiles().append(os.path.relpath(actuators, start=os.path.dirname(paths.SETUP_SO)))

    # Add StaticOptimization analysis to the tool
    so_analyze_tool.updAnalysisSet().cloneAndAppend(so)

    # Configure analyze tool
    so_analyze_tool.setReplaceForceSet(False)
    so_analyze_tool.setStartTime(paths.TIME_RANGE[0])
    so_analyze_tool.setFinalTime(paths.TIME_RANGE[1])

    # Set results directory
    so_analyze_tool.setResultsDir(utils.rel_path(paths.SO_OUTPUT, paths.SETUP_SO))

    # Print configuration to XML file
    so_analyze_tool.printToXML(paths.SETUP_SO)
    print("\n \n Static Optimization setup saved to:", paths.SETUP_SO)
    
    # run the Static Optimization
    so_analyze_tool = osim.AnalyzeTool(paths.SETUP_SO)
    so_analyze_tool.setModel(model)
    try:
        breakpoint()
        output = so_analyze_tool.run()
        print(f"Static Optimization calculation completed. Results saved to {resultsDir}")
        print(f"Output file: {output}")
    except Exception as e:
        print(f"Error during Static Optimization: {e}")

if __name__ == '__main__':
    
    start_time = time.time()
    
    if not os.path.exists(paths.USED_MODEL):
        raise FileNotFoundError(f"OpenSim model file not found: {paths.USED_MODEL}")
    
    if not os.path.exists(paths.ACTUATORS_SO):
        shutil.copy(paths.GENERIC_ACTUATORS_SO, paths.ACTUATORS_SO)
        
    if not os.path.exists(paths.SETUP_SO):
        shutil.copy(paths.GENERIC_SETUP_SO, paths.SETUP_SO)
    
    # Run the Static Optimization
    run_SO(osim_modelPath=paths.USED_MODEL, ik_output=paths.IK_OUTPUT, grf_xml=paths.GRF_XML, 
           actuators= paths.ACTUATORS_SO, resultsDir=paths.SO_OUTPUT)
    
    print(f"Static Optimization completed. Results are saved in {paths.SO_OUTPUT}")
    print(f"Execution time: {time.time() - start_time:.2f} seconds")
