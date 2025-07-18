import os
import paths
import shutil
import utils
import run_ik, run_id, run_so, run_ma, run_jra, copy_setups_to_trial, check_mom_arms
import normalise_emg


def main(trial: paths.Trial, replace: bool = False):

    # 2. Run IK
    if True:
        output_file = trial.outputFiles['IK'].abspath()
        try:

            if not os.path.exists(output_file) or replace:
                # breakpoint()  # This will pause the execution for debugging
                run_ik.main(osim_modelPath=trial.USED_MODEL,
                            marker_trc=trial.inputFiles['MARKERS'].output,
                            ik_output=output_file,
                            setup_xml=trial.path + '\\' + trial.outputFiles['IK'].setup,
                            time_range=trial.TIME_RANGE,
                            resultsDir=trial.path)

                utils.print_to_log(f'[Success] Inverse Kinematics completed. Results are saved in {output_file}')
            else:
                utils.print_to_log(f'[Info] Inverse Kinematics results already exist. Skipping computation. {output_file}')
        except Exception as e:
            utils.print_to_log(f'[Error] during Inverse Kinematics: {e}')

    # 3. Run ID
    if True:
        output_file = trial.outputFiles['ID'].abspath()
        try:
            
            # Check if the IK output file exists
            if not os.path.exists(output_file) or replace:               
                # breakpoint()  # This will pause the execution for debugging
                run_id.main(osim_modelPath=trial.USED_MODEL,
                            ik_output=trial.outputFiles['IK'].abspath(),
                            grf_xml=trial.inputFiles['GRF_XML'].abspath(),
                            setup_xml=trial.path + '\\'+ trial.outputFiles['ID'].setup,
                            resultsDir=trial.path)

                utils.print_to_log(f'[Success] Inverse Dynamics completed. Results are saved in {output_file}')
            else:
                utils.print_to_log(f'[Info] Inverse Dynamics results already exist. Skipping computation. {output_file}')

        except Exception as e:
            utils.print_to_log(f'[Error] during Inverse Dynamics: {e}')
            exit()

    # 4. Run muscle analysis
    if True:
        try:
            if not os.path.exists(trial.outputFiles['MA'].abspath()) or replace:
                run_ma.main(osim_modelPath=trial.USED_MODEL,
                            ik_output=trial.outputFiles['IK'].abspath(),
                            grf_xml=trial.inputFiles['GRF_XML'].abspath(),
                            setup_xml=trial.path + '\\' + trial.outputFiles['MA'].setup,
                            resultsDir=trial.outputFiles['MA'].abspath())

                ouput_files = trial.outputFiles['MA'].abspath()
                utils.print_to_log(f'[Success] Muscle Analysis completed. Results are saved in {ouput_files}')
        except Exception as e:
            utils.print_to_log(f'[Error] during Muscle Analysis: {e}')
            exit()

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
        utils.print_to_log(f'[Success] Muscle moment arms checked. Results are saved in {ouput_files}')

    # 5. Run Static Optimization
    if True:

        try:
            # Check if the Static Optimization output file exists
            if not os.path.exists(trial.outputFiles['SO'].abspath()) or replace:
                run_so.main(osim_modelPath=trial.USED_MODEL,
                            ik_output=trial.outputFiles['IK'].abspath(),
                            grf_xml=trial.inputFiles['GRF_XML'].abspath(),
                            setup_xml=trial.path + '\\' + trial.outputFiles['SO'].setup,
                            actuators=trial.inputFiles['ACTUATORS_SO'].abspath(),
                            resultsDir= trial.path + '\\' + trial.outputFiles['SO'].output)

                utils.print_to_log(f'[Success] Static Optimization completed. Results are saved in {trial.outputFiles["SO"].abspath()}')
                
        except Exception as e:
            utils.print_to_log(f'[Error] during Static Optimization : {e}')
            exit()

        ouput_files = trial.outputFiles['SO'].abspath()
        utils.print_to_log(f'Static Optimization completed. Results are saved in {ouput_files}')

    # 6 run Joint Reaction Analysis
    if True:
        if True:

            try:
                utils.print_to_log(f'Running JRA on: {trial.subject} / {trial.name} / {trial.USED_MODEL}')
                # breakpoint()
                run_jra.run_jra(modelpath=trial.USED_MODEL,
                                coordinates_file = trial.outputFiles['IK'].abspath(),
                                externalloadsfile = trial.inputFiles['GRF_XML'].abspath(),
                                setupJRA = trial.path + '\\' + trial.outputFiles['JRA'].setup,
                                actuators=None,
                                muscle_forces = trial.outputFiles['FORCES_SO'].abspath(),
                                results_directory=os.path.dirname(trial.outputFiles['JRA'].abspath()))

                ouput_files = trial.outputFiles['JRA'].abspath()
                utils.print_to_log(f'Joint Reaction Analysis completed. Results are saved in {ouput_files}')

            except Exception as e:
                utils.print_to_log(f'Error during Joint Reaction Analysis: {e}')

        if False:
            run_jra.run_jra_setup(modelpath=trial.USED_MODEL,
                                setupJRA=trial.SETUP_JRA)

    # Normalise EMG data
    if False:
        
        utils.print_to_log(f'Normalising EMG data for: {trial.subject} / {trial.name}')
        emg_normalise_list = []
        
        for name in paths.Settings().TRIAL_TO_ANALYSE:

            abs_path_emg = trial.inputFiles['EMG_MOT'].abspath()
            if os.path.exists(abs_path_emg):
                emg_normalise_list.append(abs_path_emg)
            else:
                print(f"EMG file not found: {abs_path_emg}")

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

                if subject.__contains__('MRI'):
                    continue

                trial.copy_inputs_to_trial(replace=False)

                utils.print_to_log(f'Running analysis for: {trial.subject} / {trial.name}')

                
                #############################################
                # Run the main analysis function
                main(trial=trial, replace=True)
                
                #############################################

                utils.print_to_log(f'Analysis completed for: {trial.subject} / {trial.name}')
