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

def main(osim_modelPath, ik_output, grf_xml, setup_xml, actuators, resultsDir):
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
    
    # load the motion data
    motion = osim.Storage(ik_output)
    
    # Create a StaticOptimization object
    so = osim.StaticOptimization()
    so.setStartTime(motion.getFirstTime())
    so.setEndTime(motion.getLastTime())
    so.setInDegrees(True)
    so.setUseMusclePhysiology(True)
    so.setUseModelForceSet(True)
    
    # Create analyze tool for static optimization
    so_analyze_tool = osim.AnalyzeTool()
    so_analyze_tool.setName("SO")

    # Set model file, motion files and external load file names
    so_analyze_tool.setModelFilename(os.path.relpath(osim_modelPath, start=os.path.dirname(setup_xml)))
    so_analyze_tool.setCoordinatesFileName(os.path.relpath(ik_output, start=os.path.dirname(setup_xml)))
    so_analyze_tool.setExternalLoadsFileName(os.path.relpath(grf_xml, start=os.path.dirname(setup_xml)))
    so_analyze_tool.setReplaceForceSet(False)
    so_analyze_tool.getForceSetFiles().append(os.path.relpath(actuators, start=os.path.dirname(setup_xml)))

    so_analyze_tool.setLowpassCutoffFrequency(6)
    # Add StaticOptimization analysis to the tool
    so_analyze_tool.updAnalysisSet().cloneAndAppend(so)

    # Configure analyze tool
    so_analyze_tool.setReplaceForceSet(False)
    so_analyze_tool.setStartTime(motion.getFirstTime())
    so_analyze_tool.setFinalTime(motion.getLastTime())

    # Set results directory
    so_analyze_tool.setResultsDir(utils.rel_path(resultsDir, resultsDir))

    # Print configuration to XML file
    so_analyze_tool.printToXML(setup_xml)
    print("\n \n Static Optimization setup saved to:", setup_xml)
    
    # change optimizer_max_iterations in the xml file
    xml = utils.read_xml(setup_xml)
    static_opt = xml.getroot().find('.//StaticOptimization/optimizer_max_iterations')
    static_opt.text = '100'  # Set to 10 iterations
    utils.save_pretty_xml(xml, setup_xml)
    
    # run the Static Optimization
    so_analyze_tool = osim.AnalyzeTool(setup_xml)
    so_analyze_tool.setModel(model)
    try:
        os.chdir(resultsDir)
        output = so_analyze_tool.run()
        print(f"Static Optimization calculation completed. Results saved to {resultsDir}")
        print(f"Output file: {output}")
    except Exception as e:
        print(f"Error during Static Optimization: {e}")

if __name__ == '__main__':
    
    base_dir = paths.SIMULATION_DIR
    subject = 'Athlete_03'  # Replace with actual subject name
    session = '22_07_06'  # Replace with actual session name
    trial = 'sq_70'  # Replace with actual trial name
    
    # create a trial instance
    trial = paths.Trial(subject_name=subject, session_name=session, trial_name=trial)
    ik_output =  trial.outputFiles['IK'].abspath()
    grf_xml = trial.inputFiles['GRF_XML'].abspath()
    setup_so = trial.path + '//' + trial.outputFiles['SO'].setup
    actuators_so = trial.inputFiles['ACTUATORS_SO'].abspath()
    so_output = trial.outputFiles['SO'].abspath()
    used_model = trial.USED_MODEL

    # trial.copy_inputs_to_trial(replace=False)
    
    print(f'osim version: {osim.__version__}')
    print(f'Running Static Optimization on model: {used_model}')
    print(f'IK output: {ik_output}')
    print(f'GRF XML: {grf_xml}')
    print(f'SO setup XML: {setup_so}')
    print(f'SO output directory: {so_output}')

    # Edit pelvis center of mass actuators
    edit_pelvis_com_actuators(used_model, actuators_so)

    # Run the Static Optimization
    main(
        osim_modelPath=used_model,
        ik_output=ik_output,
        grf_xml=grf_xml,
        setup_xml=setup_so,
        actuators=actuators_so,
        resultsDir=so_output
    )

    print(f"Static Optimization completed. Results are saved in {so_output}")
    utils.print_to_log(f'[Success] Static Optimization completed. Results are saved in {so_output}')
    
