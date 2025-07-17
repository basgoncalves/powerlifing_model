import os
import paths
import shutil
import utils
import run_ik, run_id, run_so, run_ma, run_jra, copy_setups_to_trial, check_mom_arms
import normalise_emg


def main(trial: paths.Trial):
    utils.print_to_log(f'Running analysis on: {trial.subject} / {trial.name} / {trial.USED_MODEL}')

    # 2. Run IK
    if False:
        utils.print_to_log(f'Running Inverse Kinematics on: {trial.subject} / {trial.name} / {trial.USED_MODEL}')
        
        run_ik.main(osim_modelPath=trial.USED_MODEL, 
                    marker_trc=trial.inputFiles['MARKERS'].output,
                    ik_output=trial.outputFiles['IK'].output, 
                    setup_xml=trial.outputFiles['IK'].setup, 
                    time_range=trial.TIME_RANGE,
                    resultsDir=trial.path)
        
        ouput_files = trial.outputFiles['IK'].abspath()
        utils.print_to_log(f'Inverse Kinematics completed. Results are saved in {ouput_files}')

    # 3. Run ID
    if True:
        
        try:
            utils.print_to_log(f'Running Inverse Dynamics on: {trial.subject} / {trial.name} / {trial.USED_MODEL}')
            
            run_id.main(osim_modelPath=trial.USED_MODEL, 
                        ik_output=trial.outputFiles['IK'].abspath(),
                        grf_xml=trial.inputFiles['GRF_XML'].abspath(), 
                        setup_xml=trial.path + '\\'+ trial.outputFiles['ID'].setup,
                        resultsDir=trial.path)
            
            ouput_files = trial.outputFiles['ID'].abspath()
            utils.print_to_log(f'Inverse Dynamics completed. Results are saved in {ouput_files}')
        except Exception as e:
            utils.print_to_log(f'Error during Inverse Dynamics: {e}')
            utils.print_to_log(f'Inverse Dynamics failed for: {trial.subject} / {trial.name} / {trial.USED_MODEL}')

    # 4. Run muscle analysis
    if False:
        try:
            utils.print_to_log(f'Running Muscle Analysis on: {trial.subject} / {trial.name} / {trial.USED_MODEL}')
            run_ma.main(osim_modelPath=trial.USED_MODEL, 
                        ik_output = trial.outputFiles['IK'].abspath(),
                        grf_xml = trial.inputFiles['GRF_XML'].abspath(), 
                        setup_xml = trial.path + '\\' + trial.outputFiles['MA'].setup,
                        resultsDir=trial.outputFiles['MA'].abspath())
            
            ouput_files = trial.outputFiles['MA'].abspath()
            utils.print_to_log(f'Muscle Analysis completed. Results are saved in {ouput_files}')
        except Exception as e:
            utils.print_to_log(f'Error during Muscle Analysis: {e}')
            utils.print_to_log(f'Muscle Analysis failed for: {trial.subject} / {trial.name} / {trial.USED_MODEL}')
            
    # 4b Check moment arms
    if False:
        utils.print_to_log(f'Checking muscle moment arms for model: {trial.USED_MODEL}')
        utils.checkMuscleMomentArms(osim_modelPath=trial.USED_MODEL, 
                                    ik_output=trial.outputFiles['IK'].abspath(),
                                    leg='l', 
                                    threshold=0.005)
        utils.checkMuscleMomentArms(osim_modelPath=trial.USED_MODEL,
                                    ik_output=trial.outputFiles['IK'].abspath(), 
                                    leg='r', 
                                    threshold=0.005)
        
        ouput_files = trial.outputFiles['MA'].abspath()
        utils.print_to_log(f'Muscle moment arms checked. Results are saved in {ouput_files}')

    # 5. Run Static Optimization
    if True:
        utils.print_to_log(f'Running Static Optimization on: {trial.subject} / {trial.name} / {trial.USED_MODEL}')
        try:
            run_so.main(osim_modelPath=trial.USED_MODEL, 
                        ik_output=trial.outputFiles['IK'].abspath(),
                        grf_xml=trial.inputFiles['GRF_XML'].abspath(), 
                        setup_xml=trial.path + '\\' + trial.outputFiles['SO'].setup,
                        actuators=trial.inputFiles['ACTUATORS_SO'].abspath(), 
                        resultsDir= trial.path + '\\' + trial.outputFiles['SO'].output)
        except Exception as e:
            utils.print_to_log(f'Error during Static Optimization : {e}')
            utils.print_to_log(f'Static Optimization failed for: {trial.subject} / {trial.name} / {trial.USED_MODEL}')
        
        ouput_files = trial.outputFiles['SO'].abspath()
        utils.print_to_log(f'Static Optimization completed. Results are saved in {ouput_files}')
        
    # 6 run Joint Reaction Analysis
    if True:
        if True:
            
            try:
                utils.print_to_log(f'Running JRA on: {trial.subject} / {trial.name} / {trial.USED_MODEL}')
                run_jra.run_jra(modelpath=trial.USED_MODEL, 
                                coordinates_file = trial.outputFiles['IK'].abspath(), 
                                externalloadsfile = trial.inputFiles['GRF_XML'].abspath(),
                                setupJRA = trial.path + '\\' + trial.outputFiles['JRA'].setup,
                                actuators=None,
                                muscle_forces = trial.path + '\\' + trial.outputFiles['SO'] + 'SO_StaticOptimization_forces.sto',
                                results_directory=os.path.dirname(trial.outputFiles['JRA'].abspath()))
                
                ouput_files = trial.outputFiles['JRA'].abspath()
                utils.print_to_log(f'Joint Reaction Analysis completed. Results are saved in {ouput_files}')
                
            except Exception as e:
                utils.print_to_log(f'Error during Joint Reaction Analysis: {e}')
                utils.print_to_log(f'Joint Reaction Analysis failed for: {trial.subject} / {trial.name} / {trial.USED_MODEL}')
                
        if False:
            run_jra.run_jra_setup(modelpath=trial.USED_MODEL, 
                                setupJRA=trial.SETUP_JRA)
        
    # Normalise EMG data
    if True:
        utils.print_to_log(f'Normalising EMG data for: {trial.subject} / {trial.name}')
        emg_normalise_list = []
        for name in paths.Settings().TRIAL_TO_ANALYSE:
        
            filepath = os.path.join(os.path.dirname(trial.path), name)
            if os.path.exists(filepath):
                emg_normalise_list.append(filepath)
            else:
                print(f"EMG file not found: {filepath}")
                
        normalise_emg.main(target_emg_path=trial.inputFiles['EMG_MOT'].abspath(),
                    normalise_emg_list=emg_normalise_list)
        
        utils.print_to_log(f'EMG data normalised. Results are saved in {trial.inputFiles["EMG_MOT_NORMALISED"].abspath()}')
        
    # 6. Run CEINMS calibration and optimization
    if False:
        utils.print_to_log(f'Running CEINMS calibration on: {trial.subject} / {trial.name}')
        try:
            import run_ceinms_calibration
            run_ceinms_calibration.main(trial.CEINMS_SETUP_CALIBRATION)
            utils.print_to_log(f'CEINMS calibration completed successfully.')
        except Exception as e:
            print(f"Error during CEINMS calibration: {e}")
            utils.print_to_log(f'Error during CEINMS calibration: {e}')

if __name__ == "__main__":
    utils.print_to_log("Starting analysis...")
    
    settings = paths.Settings()
    analysis = paths.Analysis()
    trial_list = settings.TRIAL_TO_ANALYSE
    
    sessions_to_skip = ['25_03_31']
    
    for subject in analysis.subject_list:
        session_list = analysis.get_subject(subject).SESSIONS
        
        for session in session_list:            
            if session.name in sessions_to_skip:
                continue
            
            for trial in session.TRIALS:
                trial.copy_inputs_to_trial(replace=False)
                
                utils.print_to_log(f'Running analysis for: {trial.subject} / {trial.name}')
                
                main(trial=trial)

                utils.print_to_log(f'Analysis completed for: {trial.subject} / {trial.name}')            
            