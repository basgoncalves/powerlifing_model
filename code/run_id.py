import os
import shutil
import opensim as osim
import paths
import utils

def main(osim_modelPath, ik_output: str, grf_xml: str, setup_xml: str, resultsDir: str):
    """
    Example usage:
    main(osim_modelPath='path/to/model.osim', 
         ik_output='path/to/ik_output.mot', 
         grf_xml='path/to/grf.xml', 
         setup_xml='path/to/setup.xml', 
         resultsDir='path/to/results')
    
    """

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
    model = osim.Model(osim_modelPath)
    model.initSystem()

    # Load the motion data
    motion = osim.Storage(ik_output)

    # Create the Inverse Dynamics tool
    idTool = osim.InverseDynamicsTool()
    idTool.setModel(model)
    idTool.setOutputGenForceFileName("inverse_dynamics.sto") # Output file name for the forces
    idTool.setModelFileName(os.path.relpath(osim_modelPath, start=os.path.dirname(setup_xml)))
    idTool.setCoordinatesFileName(os.path.relpath(ik_output, start=os.path.dirname(setup_xml)))
    idTool.setStartTime(motion.getFirstTime()) # Start time
    idTool.setEndTime(motion.getLastTime()) # end time
    idTool.setExternalLoadsFileName(os.path.relpath(grf_xml, start=os.path.dirname(setup_xml)))
    idTool.setResultsDir(resultsDir) # results directory 
    
    # Set lowpass filter frequency
    idTool.setLowpassCutoffFrequency(6)
    
    # Print the setup to XML
    idTool.printToXML(setup_xml)
    print(f"Inverse Dynamics setup saved to {setup_xml}")
    
    # Load xml and edit forces to exclude
    xml = utils.read_xml(setup_xml)
    xml.find('.//forces_to_exclude').text = 'Muscles'
    utils.save_pretty_xml(xml, setup_xml)

    # Reload tool from xml
    idTool = osim.InverseDynamicsTool(setup_xml)   
    idTool.printToXML(setup_xml)  # Print to XML again to ensure changes are saved
    
    # breakpoint()  # Optional: pause execution for debugging 
    # Run the inverse dynamics calculation
    os.chdir(resultsDir)
    idTool.run()
    idTool.setModel(model)  # Set the model again after running
    
    print(f"Inverse Dynamics calculation completed. Results saved to {resultsDir}")

if __name__ == '__main__':
   
    base_dir = paths.SIMULATION_DIR
    subject = 'Athlete_03'  # Replace with actual subject name
    session = '22_07_06'  # Replace with actual session name
    trial = 'dl_70'  # Replace with actual trial name
    
    # create a trial instance
    trial = paths.Trial(subject_name=subject, session_name=session, trial_name=trial)

    setup_xml = os.path.join(trial.path, trial.outputFiles['ID'].setup)
    if not os.path.exists(setup_xml):
        shutil.copyfile(src= os.path.join(paths.SETUP_DIR, trial.outputFiles['ID'].setup), 
                        dst=setup_xml)
        
    osim_modelPath = trial.USED_MODEL
    ik_mot = trial.outputFiles['IK'].abspath()
    setup_id = trial.path + '\\' + trial.outputFiles['ID'].setup
    grf_xml = trial.inputFiles['GRF_XML'].abspath()

    if not os.path.exists(grf_xml):
        shutil.copyfile(src= os.path.join(paths.SETUP_DIR, trial.inputFiles['GRF_XML'].output), 
                        dst=grf_xml)
    
    main(osim_modelPath=osim_modelPath,
            ik_output=ik_mot,
            grf_xml=grf_xml,
            setup_xml=setup_id,
            resultsDir=trial.path)
    
    
