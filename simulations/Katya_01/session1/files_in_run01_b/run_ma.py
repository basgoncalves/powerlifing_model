import os
import opensim as osim
from pathlib import Path

def run_MA(osim_modelPath, ik_mot, grf_xml, resultsDir):
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

    # Create a MuscleAnalysis object
    muscleAnalysis = osim.MuscleAnalysis()
    muscleAnalysis.setModel(model)
    muscleAnalysis.setStartTime(motion.getFirstTime())
    muscleAnalysis.setEndTime(motion.getLastTime())

    # Create the muscle analysis tool
    maTool = osim.AnalyzeTool()
    maTool.setModel(model)
    maTool.setModelFilename(osim_modelPath)
    maTool.setLowpassCutoffFrequency(6)
    maTool.setCoordinatesFileName(ik_mot)
    maTool.setName('')
    maTool.setMaximumNumberOfSteps(20000)
    maTool.setStartTime(motion.getFirstTime())
    maTool.setFinalTime(motion.getLastTime())
    maTool.getAnalysisSet().cloneAndAppend(muscleAnalysis)
    maTool.setResultsDir(resultsDir)
    maTool.setInitialTime(motion.getFirstTime())
    maTool.setFinalTime(motion.getLastTime())
    maTool.setExternalLoadsFileName(grf_xml)
    maTool.setSolveForEquilibrium(False)
    maTool.setReplaceForceSet(False)
    maTool.setMaximumNumberOfSteps(20000)
    maTool.setOutputPrecision(8)
    maTool.setMaxDT(1)
    maTool.setMinDT(1e-008)
    maTool.setErrorTolerance(1e-005)
    maTool.removeControllerSetFromModel()
    maTool.printToXML(os.path.join(resultsDir, '..', 'setup_ma.xml'))

    # Reload analysis from xml
    maTool = osim.AnalyzeTool(os.path.join(resultsDir, '..', 'setup_ma.xml'))
    maTool.getModel().initSystem()
    # Run the muscle analysis calculation
    maTool.run()

if __name__ == '__main__':
    current_path = Path(__file__).parent.resolve()
    osim_modelPath = Path(current_path, 'P01_pers.osim')
    ik_mot = Path(current_path, 'IK_half_cycle.mot')
    grf_xml = Path(current_path, 'Right_1.xml')

    # Define the results directory
    resultsDir = os.path.join(current_path, 'muscleAnalysis')
    
    # Run the Muscle Analysis
    run_MA(osim_modelPath.__str__(), ik_mot.__str__(), grf_xml.__str__(), resultsDir)
    
    print(f"Muscle Analysis completed. Results are saved in {resultsDir}")


