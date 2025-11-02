import inspect
import os
import shutil
import sys
import opensim as osim
import utils
import settings


def main(osimModelPath=None, ikOutputPath=None, grfXmlPath=None, setupXmlPath=None, resultsDir=None):
    """
    Example usage:
    main(osim_modelPath='path/to/model.osim', 
         ik_output='path/to/ik_output.mot', 
         grf_xml='path/to/grf.xml', 
         setup_xml='path/to/setup.xml', 
         resultsDir='path/to/results')
    
    """
    # check if any input is empty and if so ask for input
    osimModelPath = utils.check_arg(osimModelPath,'osimModelPath')
    ikOutputPath = utils.check_arg(ikOutputPath,'ikOutputPath')
    grfXmlPath = utils.check_arg(grfXmlPath,'grfXmlPath')
    setupXmlPath = utils.check_arg(setupXmlPath,'setupXmlPath')
    resultsDir = utils.check_arg(resultsDir,'resultsDir')

    if not os.path.exists(resultsDir):
        os.makedirs(resultsDir)

    if not os.path.exists(osimModelPath):
        raise FileNotFoundError(f"OpenSim model file not found: {osimModelPath}")
    
    if not os.path.exists(ikOutputPath):
        raise FileNotFoundError(f"Inverse Kinematics motion file not found: {ikOutputPath}")

    if not os.path.exists(grfXmlPath):
        raise FileNotFoundError(f"Ground Reaction Forces XML file not found: {grfXmlPath}")

    # Load the model
    print(f"Loading OpenSim model from {osimModelPath}")
    model = osim.Model(osimModelPath)
    model.initSystem()

    # Load the motion data
    motion = osim.Storage(ikOutputPath)

    # Create the Inverse Dynamics tool
    idTool = osim.InverseDynamicsTool()
    idTool.setModel(model)
    idTool.setOutputGenForceFileName("inverse_dynamics.sto") # Output file name for the forces
    idTool.setModelFileName(os.path.relpath(osimModelPath, start=os.path.dirname(setupXmlPath)))
    idTool.setCoordinatesFileName(os.path.relpath(ikOutputPath, start=os.path.dirname(setupXmlPath)))
    idTool.setStartTime(motion.getFirstTime()) # Start time
    idTool.setEndTime(motion.getLastTime()) # end time
    idTool.setExternalLoadsFileName(os.path.relpath(grfXmlPath, start=os.path.dirname(setupXmlPath)))
    idTool.setResultsDir(resultsDir) # results directory 
    
    # Set lowpass filter frequency
    idTool.setLowpassCutoffFrequency(6)
    
    # Print the setup to XML
    idTool.printToXML(setupXmlPath)
    print(f"Inverse Dynamics setup saved to {setupXmlPath}")
    
    # Load xml and edit forces to exclude
    xml = utils.read_xml(setupXmlPath)
    xml.find('.//forces_to_exclude').text = 'Muscles'
    utils.save_pretty_xml(xml, setupXmlPath)

    # Reload tool from xml
    idTool = osim.InverseDynamicsTool(setupXmlPath)   
    idTool.printToXML(setupXmlPath)  # Print to XML again to ensure changes are saved
    
    # breakpoint()  # Optional: pause execution for debugging 
    # Run the inverse dynamics calculation
    os.chdir(resultsDir)
    idTool.run()
    idTool.setModel(model)  # Set the model again after running

    print(f"Inverse Dynamics calculation completed. Results saved to {resultsDir}\\inverse_dynamics.sto")

if __name__ == '__main__':

    # create a trial instance
    trial = utils.Trial(subject_name=settings.subject,
                        session_name=settings.session,
                        trial_name=settings.trial)
        
    osim_modelPath = str(settings.osimModelPath)
    ik_output = str(trial.outputFiles.IK)
    setup_id = str(trial.setupFiles.ID)
    grf_xml = str(trial.setupFiles.GRF)
    
    if not os.path.exists(setup_id):    
        shutil.copyfile(src=os.path.join(settings.SETUP_DIR, settings.SetupFiles().ID), 
                        dst=setup_id)

    if not os.path.exists(grf_xml):
        shutil.copyfile(src= os.path.join(settings.SETUP_DIR, settings.SetupFiles().GRF), 
                        dst=grf_xml)

    main(osimModelPath=osim_modelPath,
            ikOutputPath=ik_output,
            grfXmlPath=grf_xml,
            setupXmlPath=setup_id,
            resultsDir=os.path.dirname(setup_id))
    
    

