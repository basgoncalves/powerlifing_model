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
    if not osimModelPath:
        osimModelPath = input("Enter the path to the OpenSim model file (.osim): ").strip('"')
    if not ikOutputPath:
        ikOutputPath = input("Enter the path to the Inverse Kinematics output file (.mot): ").strip('"')
    if not grfXmlPath:
        grfXmlPath = input("Enter the path to the Ground Reaction Forces XML file (.xml): ").strip('"')
    if not setupXmlPath:
        setupXmlPath = input("Enter the path to save the Inverse Dynamics setup XML file (.xml): ").strip('"')

    if not resultsDir:
        resultsDir = os.path.dirname(setupXmlPath)
    
    if not os.path.exists(osimModelPath):
        raise FileNotFoundError(f"OpenSim model file not found: {osimModelPath}")
    
    if not os.path.exists(ikOutputPath):
        raise FileNotFoundError(f"Inverse Kinematics motion file not found: {ikOutputPath}")

    if not os.path.exists(grfXmlPath):
        raise FileNotFoundError(f"Ground Reaction Forces XML file not found: {grfXmlPath}")
    
    if not os.path.exists(resultsDir):
        os.makedirs(resultsDir)
    
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
    idTool.setResultsDir(os.path.relpath(resultsDir, start=os.path.dirname(setupXmlPath)))
    
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

    main()
    
    

