import os
import opensim as osim
import paths

def run_ID(osim_modelPath, ik_mot, grf_xml, setup_xml):
    
    resultsDir = os.path.dirname(setup_xml)
    if not os.path.exists(resultsDir):
        os.makedirs(resultsDir)

    if not os.path.exists(osim_modelPath):
        raise FileNotFoundError(f"OpenSim model file not found: {osim_modelPath}")
    
    if not os.path.exists(ik_mot):
        raise FileNotFoundError(f"Inverse Kinematics motion file not found: {ik_mot}")
    
    if not os.path.exists(grf_xml):
        raise FileNotFoundError(f"Ground Reaction Forces XML file not found: {grf_xml}")
    
    # Load the model
    print(f"Loading OpenSim model from {osim_modelPath}")
    model = osim.Model(osim_modelPath)
    model.initSystem()

    # Load the motion data
    motion = osim.Storage(ik_mot)

    # Create the Inverse Dynamics tool
    idTool = osim.InverseDynamicsTool()
    idTool.setModel(model)
    idTool.setModelFileName(osim_modelPath)
    idTool.setCoordinatesFileName(str(ik_mot))
    idTool.setStartTime(motion.getFirstTime())
    idTool.setEndTime(motion.getLastTime())
    idTool.setExternalLoadsFileName(str(grf_xml))
    idTool.setResultsDir(resultsDir)
    idTool.setOutputGenForceFileName("inverse_dynamics.sto")
    idTool.printToXML(setup_xml)
    print(f"Inverse Dynamics setup saved to {setup_xml}")

    # Reload tool from xml
    idTool = osim.InverseDynamicsTool(setup_xml)    
    # Run the inverse dynamics calculation
    idTool.run()
    
    print(f"Inverse Dynamics calculation completed. Results saved to {resultsDir}")

if __name__ == '__main__':
   
    osim_modelPath = paths.USED_MODEL
    ik_mot = paths.IK_OUTPUT
    grf_xml = paths.GRF_XML
    setup_id = paths.SETUP_ID
    
    print(f'osim version: {osim.__version__}')
    
    run_ID(osim_modelPath, ik_mot, grf_xml, setup_id)
