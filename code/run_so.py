import os
import shutil
import opensim as osim
import paths
import utils
import time


def edit_pelvis_com_actuators(modelFilePath, actuatorsFilePath):
    """
    Edit the pelvis center of mass actuator in the OpenSim model.
    """ 
    model = osim.Model(modelFilePath)
    model.initSystem()

    # Find the pelvis center of mass actuator
    pelvis = model.getBodySet().get('pelvis')
    com = pelvis.get_mass_center().to_numpy()

    actuators = utils.read_xml(actuatorsFilePath)
    point_actuators = actuators.find('ForceSet').find('objects').findall('PointActuator')
    
    for actuator in point_actuators:
        if actuator.get('name') in ['FX', 'FY', 'FZ']:
            # Update the point in the actuator to match the pelvis center of mass
            point = actuator.find('point')
            point.text = f"{com[0]} {com[1]} {com[2]}"
    
    # Save the modified actuators file
    utils.save_pretty_xml(actuators, actuatorsFilePath)
    
    print(f"Updated pelvis center of mass actuator in {actuatorsFilePath} to {com}")

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

    so_analyze_tool.setLowpassCutoffFrequency(6)
    # Add StaticOptimization analysis to the tool
    so_analyze_tool.updAnalysisSet().cloneAndAppend(so)

    # Configure analyze tool
    so_analyze_tool.setReplaceForceSet(False)
    so_analyze_tool.setStartTime(paths.TIME_RANGE[0])
    so_analyze_tool.setFinalTime(paths.TIME_RANGE[1])
    
    # Set results directory
    so_analyze_tool.setResultsDir(utils.rel_path(resultsDir, resultsDir))

    # Print configuration to XML file
    so_analyze_tool.printToXML(paths.SETUP_SO)
    print("\n \n Static Optimization setup saved to:", paths.SETUP_SO)
    
    # change optimizer_max_iterations in the xml file
    xml = utils.read_xml(paths.SETUP_SO)
    static_opt = xml.getroot().find('.//StaticOptimization/optimizer_max_iterations')
    static_opt.text = '10'  # Set to 10 iterations
    utils.save_pretty_xml(xml, paths.SETUP_SO)
    
    # run the Static Optimization
    so_analyze_tool = osim.AnalyzeTool(paths.SETUP_SO)
    so_analyze_tool.setModel(model)
    try:
        os.chdir(resultsDir)
        output = so_analyze_tool.run()
        print(f"Static Optimization calculation completed. Results saved to {resultsDir}")
        print(f"Output file: {output}")
    except Exception as e:
        print(f"Error during Static Optimization: {e}")

if __name__ == '__main__':
    
    start_time = time.time()
    
    utils.print_to_log(f'Running Static Optimization on: {paths.SUBJECT} / {paths.TRIAL_NAME} / {paths.USED_MODEL}')
    
    if not os.path.exists(paths.USED_MODEL):
        raise FileNotFoundError(f"OpenSim model file not found: {paths.USED_MODEL}")
    
    if not os.path.exists(paths.ACTUATORS_SO):
        shutil.copy(paths.GENERIC_ACTUATORS_SO, paths.ACTUATORS_SO)
        
    if not os.path.exists(paths.SETUP_SO):
        shutil.copy(paths.GENERIC_SETUP_SO, paths.SETUP_SO)
        
    # Edit pelvis center of mass actuator
    edit_pelvis_com_actuators(paths.USED_MODEL, paths.ACTUATORS_SO)
    
    # Run the Static Optimization
    run_SO(osim_modelPath=paths.USED_MODEL, 
           ik_output=paths.IK_OUTPUT, 
           grf_xml=paths.GRF_XML, 
           actuators= paths.ACTUATORS_SO, 
           resultsDir=paths.SO_OUTPUT)
    
    print(f"Static Optimization completed. Results are saved in {paths.SO_OUTPUT}")
    print(f"Execution time: {time.time() - start_time:.2f} seconds")
    utils.print_to_log(f"Static Optimization completed. Results are saved in {paths.SO_OUTPUT}")
