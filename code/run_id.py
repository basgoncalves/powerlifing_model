import os
import shutil
import opensim as osim
import paths

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
        print(f"OpenSim model file not found: {osim_modelPath}")
        return None
    
    if not os.path.exists(ik_output):
        print(f"Inverse Kinematics motion file not found: {ik_output}")
        return None
    
    if not os.path.exists(grf_xml):
        print(f"Ground Reaction Forces XML file not found: {grf_xml}")
        return None
    
    # Load the model
    print(f"Loading OpenSim model from {osim_modelPath}")
    model = osim.Model(osim_modelPath)
    model.initSystem()

    # Load the motion data
    motion = osim.Storage(ik_output)

    # Create the Inverse Dynamics tool
    idTool = osim.InverseDynamicsTool()
    idTool.setModel(model)
    idTool.setModelFileName(osim_modelPath)
    idTool.setCoordinatesFileName(str(ik_output))
    idTool.setStartTime(motion.getFirstTime())
    idTool.setEndTime(motion.getLastTime())
    idTool.setExternalLoadsFileName(str(grf_xml))
    idTool.setResultsDir(resultsDir)
    idTool.setLowpassCutoffFrequency(6)
    idTool.setOutputGenForceFileName("inverse_dynamics.sto")
    idTool.printToXML(setup_xml)
    print(f"Inverse Dynamics setup saved to {setup_xml}")

    # Reload tool from xml
    idTool = osim.InverseDynamicsTool(setup_xml)    
    # Run the inverse dynamics calculation
    os.chdir(resultsDir)
    idTool.run()
    
    print(f"Inverse Dynamics calculation completed. Results saved to {resultsDir}")

if __name__ == '__main__':
   
    osim_modelPath = paths.USED_MODEL
    ik_mot = paths.IK_OUTPUT
    grf_xml = paths.GRF_XML
    setup_id = paths.SETUP_ID
    
    # copy template setup file to trial directory
    if not os.path.exists(setup_id):
        shutil.copy(paths.GENERIC_SETUP_ID, setup_id)
        
    if not os.path.exists(grf_xml):
        shutil.copy(paths.GENERIC_GRF_XML, grf_xml)
    print(f'osim version: {osim.__version__}')
    
    try:
        main(osim_modelPath, ik_mot, grf_xml, setup_id)
    except Exception as e:
        print(f"Error during Inverse Dynamics: {e}")
    print("Inverse Dynamics run completed.")
    
    
