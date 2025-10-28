import os
import time
import opensim as osim
import settings
import utils

def main(osim_modelPath, ik_output, grf_xml, setup_xml, resultsDir):
    
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
    
    
    trial = utils.Trial(subject_name=settings.subject,
                        session_name=settings.session,
                        trial_name=settings.trial)
    
    trial.copy_inputs_to_trial(replace=False)
    
    osim_modelPath = str(trial.inputFiles.osimModel)
    
    print(f'osim version: {osim.__version__}')
    print(f'Running Muscle Analysis on model: {osim_modelPath}')
    time.sleep(1)  # Optional: wait for a second before running the analysis
    
    ####################################### Run the Muscle Analysis #####################################
    main(osim_modelPath, 
         ik_output=str(trial.outputFiles.IK), 
         grf_xml=str(trial.setupFiles.GRF), 
         setup_xml=str(trial.setupFiles.MA),
         resultsDir= str(trial.outputFiles.MA))
    
    outputFilesPath = os.path.join(trial.path, 'MuscleAnalysis')
    utils.print_to_log(f'Muscle Analysis completed. Results are saved in {outputFilesPath}')


