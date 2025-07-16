import os
import time
import opensim as osim
import paths
import utils

def run_MA(osim_modelPath, ik_output, grf_xml, resultsDir):
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

    # Create a MuscleAnalysis object
    muscleAnalysis = osim.MuscleAnalysis()
    muscleAnalysis.setModel(model)
    muscleAnalysis.setStartTime(motion.getFirstTime())
    muscleAnalysis.setEndTime(motion.getLastTime())

    # Create the muscle analysis tool
    maTool = osim.AnalyzeTool()
    maTool.setModel(model)
    maTool.setModelFilename(os.path.relpath(osim_modelPath, start=os.path.dirname(paths.SETUP_MA)))
    maTool.setLowpassCutoffFrequency(6)
    maTool.setCoordinatesFileName(os.path.relpath(ik_output, start=os.path.dirname(paths.SETUP_MA)))
    maTool.setName('')
    maTool.setMaximumNumberOfSteps(20000)
    maTool.setStartTime(motion.getFirstTime())
    maTool.setFinalTime(motion.getLastTime())
    maTool.getAnalysisSet().cloneAndAppend(muscleAnalysis)
    maTool.setResultsDir(os.path.relpath(resultsDir, start=os.path.dirname(paths.SETUP_MA)))
    maTool.setInitialTime(motion.getFirstTime())
    maTool.setFinalTime(motion.getLastTime())
    maTool.setExternalLoadsFileName(os.path.relpath(grf_xml, start=os.path.dirname(paths.SETUP_MA)))
    maTool.setSolveForEquilibrium(False)
    maTool.setReplaceForceSet(False)
    maTool.setMaximumNumberOfSteps(20000)
    maTool.setOutputPrecision(8)
    maTool.setMaxDT(1)
    maTool.setMinDT(1e-008)
    maTool.setErrorTolerance(1e-005)
    maTool.removeControllerSetFromModel()
    maTool.setLowpassCutoffFrequency(6)
    maTool.printToXML(paths.SETUP_MA)

    # Reload analysis from xml
    maTool = osim.AnalyzeTool(paths.SETUP_MA)
    maTool.getModel().initSystem()
    # Run the muscle analysis calculation
    maTool.run()

if __name__ == '__main__':
    osim_modelPath = paths.USED_MODEL
    
    print(f'osim version: {osim.__version__}')
    print(f'Running Muscle Analysis on model: {osim_modelPath}')
    time.sleep(1)  # Optional: wait for a second before running the analysis
    
    if not os.path.exists(osim_modelPath):
        raise FileNotFoundError(f"OpenSim model file not found: {osim_modelPath}")

    if not os.path.exists(paths.IK_OUTPUT):
        print(f"Inverse Kinematics motion file not found: {paths.IK_OUTPUT}")
        time.sleep(1)
        import run_ik
        
        run_ik.run_IK(osim_modelPath=paths.USED_MODEL, marker_trc=paths.MARKERS_TRC, 
                      ik_output=paths.IK_OUTPUT, setup_xml=paths.SETUP_IK, time_range=paths.TIME_RANGE)
    
    if not os.path.exists(paths.ID_OUTPUT):
        print(f"Ground Reaction Forces XML file not found: {paths.GRF_XML}")
        time.sleep(1)
        import run_id
        
        run_id.run_ID(osim_modelPath=paths.USED_MODEL, ik_mot=paths.IK_OUTPUT, 
                      grf_xml=paths.GRF_XML, setup_xml=paths.SETUP_ID)
    
    # Run the Muscle Analysis
    run_MA(osim_modelPath, ik_output=paths.IK_OUTPUT, grf_xml=paths.GRF_XML, resultsDir=paths.MA_OUTPUT)
    
    print(f"Muscle Analysis completed. Results are saved in {paths.MA_OUTPUT}")


