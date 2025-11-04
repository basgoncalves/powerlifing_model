import os
import time
import opensim as osim
import settings
import utils

def main(osim_modelPath=None, ik_output=None, 
         grf_xml=None, setup_xml=None, resultsDir=None):

    if osim_modelPath is None:
        osim_modelPath = input("Enter the path to the OpenSim model file (.osim): ").strip('"')
    if ik_output is None:
        ik_output = input("Enter the desired output path for the IK results (.mot): ").strip('"')
    if grf_xml is None:
        grf_xml = input("Enter the path to the GRF XML file (.xml): ").strip('"')
    if setup_xml is None:
        setup_xml = input("Enter the path to the setup XML file (.xml): ").strip('"')
    if resultsDir is None:
        resultsDir = os.path.dirname(ik_output)

    if not os.path.exists(osim_modelPath):
        raise FileNotFoundError(f"OpenSim model file not found: {osim_modelPath}")
    
    if not os.path.exists(ik_output):
        raise FileNotFoundError(f"Inverse Kinematics motion file not found: {ik_output}")
    
    if not os.path.exists(grf_xml):
        raise FileNotFoundError(f"Ground Reaction Forces XML file not found: {grf_xml}")
    
    if not resultsDir:
        resultsDir = os.path.dirname(ik_output)
    
    if not os.path.exists(resultsDir):
        os.makedirs(resultsDir, exist_ok=True)
    
    # Load the model
    print(f"Loading OpenSim model from {osim_modelPath}")
    model = osim.Model(osim_modelPath)
    model.initSystem()

    # Load the motion data
    motion = osim.Storage(ik_output)

    # Create a MuscleAnalysis object
    muscleAnalysis = osim.MuscleAnalysis()
    muscleAnalysis.setModel(model)
    muscleAnalysis.setStartTime(motion.getFirstTime())
    muscleAnalysis.setEndTime(motion.getLastTime())

    # Create the muscle analysis tool
    maTool = osim.AnalyzeTool()
    maTool.setModel(model)
    maTool.setModelFilename(os.path.relpath(osim_modelPath,  start=os.path.dirname(setup_xml)))
    maTool.setLowpassCutoffFrequency(6)
    maTool.setCoordinatesFileName(os.path.relpath(ik_output, start=os.path.dirname(setup_xml)))
    maTool.setName('')
    maTool.setMaximumNumberOfSteps(20000)
    maTool.setStartTime(motion.getFirstTime())
    maTool.setFinalTime(motion.getLastTime())
    maTool.getAnalysisSet().cloneAndAppend(muscleAnalysis)
    maTool.setResultsDir(os.path.relpath(resultsDir, start=os.path.dirname(setup_xml)))
    maTool.setInitialTime(motion.getFirstTime())
    maTool.setFinalTime(motion.getLastTime())
    maTool.setExternalLoadsFileName(os.path.relpath(grf_xml, start=os.path.dirname(setup_xml)))
    maTool.setSolveForEquilibrium(False)
    maTool.setReplaceForceSet(False)
    maTool.setMaximumNumberOfSteps(20000)
    maTool.setOutputPrecision(8)
    maTool.setMaxDT(1)
    maTool.setMinDT(1e-008)
    maTool.setErrorTolerance(1e-005)
    maTool.removeControllerSetFromModel()
    maTool.setLowpassCutoffFrequency(6)
    maTool.printToXML(setup_xml)

    # Reload analysis from xml
    maTool = osim.AnalyzeTool(setup_xml)
    maTool.getModel().initSystem()
    # Run the muscle analysis calculation
    maTool.run()

if __name__ == '__main__':
    
    
    main()
