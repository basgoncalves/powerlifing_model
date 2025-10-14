import os
import subprocess
import time
import paths
import shutil
import utils
import run_ik, run_id, run_so, run_ma, run_jra
import run_emg_normalise
import exportC3D, compare_marker_locations, calculate_muscle_moments


run = {'reset':False,
       'INCREASE_MUSCLE_FORCE': False,
       'exportC3D': False,
       'IK': False,
       'ID': False,
       'MA': False,
       'SO': False,
       'JRA': False,
       'EMG_NORMALISE': False,
       'CREATE_EXCITATION_GENERATOR': False,
       'CEINMS_CALIBRATION': False,
       'CEINMS_OPTIMISATION': False,
       'MOMENT_ARMS': False,}


def main(trial: utils.Trial, replace: bool = False):

    # Reset trials to only input files
    if run['reset']:
        trial.reset()

    # Increase muscle force
    if run['INCREASE_MUSCLE_FORCE']:
        trial.increase_muscle_force(factor=3, replace=replace)

    # Export c3d file
    if run['exportC3D']:
        subject_without_zero = trial.subject.replace('0', '')
        exportC3D.export_markers(trial.inputFiles['C3D'].abspath(),
                                strings_to_remove = ['Bar:', f'{subject_without_zero}:'])
        exportC3D.export_grf(trial.inputFiles['C3D'].abspath())
        exportC3D.export_emg(trial.inputFiles['C3D'].abspath())

    # 2. Run IK
    if run['IK']:
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

        try:
            virtual_marker_locations = trial.path + '\\' + '_ik_model_marker_locations.sto'
            compare_marker_locations.main(marker_experimental_path=trial.inputFiles['MARKERS'].abspath(),
                                          marker_virtual_path=virtual_marker_locations)
            utils.print_to_log(f'[Success] Marker location comparison completed.')
        except:
            utils.print_to_log(f'[Error] during marker location comparison')

    # 3. Run ID
    if run['ID']:
        output_file = trial.outputFiles['ID'].abspath()
        try:

            # Check if the IK output file exists
            if not os.path.exists(output_file) or replace:
                # breakpoint()  # This will pause the execution for debugging
                run_id.main(osimModelPath=trial.USED_MODEL,
                            ikOutputPath=trial.outputFiles['IK'].abspath(),
                            grfXmlPath=trial.inputFiles['GRF_XML'].abspath(),
                            setupXmlPath=trial.path + '\\'+ trial.outputFiles['ID'].setup,
                            resultsDir=trial.path)

                utils.print_to_log(f'[Success] Inverse Dynamics completed. Results are saved in {output_file}')
            else:
                utils.print_to_log(f'[Info] Inverse Dynamics results already exist. Skipping computation. {output_file}')

        except Exception as e:
            utils.print_to_log(f'[Error] during Inverse Dynamics: {e}')
            exit()

    # 4. Run muscle analysis
    if run['MA']:
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

    # 5. Check moment arms
    if run['MOMENT_ARMS']:
        try:
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
        except Exception as e:
            utils.print_to_log(f'[Error] during Muscle moment arms check: {e}')

    # 6. Run Static Optimization
    if run['SO']:

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

    # 7. Run Joint Reaction Analysis
    if run['JRA']:
        if True:
            try:
                utils.print_to_log(f'Running JRA on: {trial.subject} / {trial.name} / {trial.USED_MODEL}')
                # breakpoint()
                run_jra.main(modelpath=trial.USED_MODEL,
                                coordinates_file = trial.outputFiles['IK'].abspath(),
                                externalloadsfile = trial.inputFiles['GRF_XML'].abspath(),
                                setupJRA = trial.path + '\\' + trial.outputFiles['JRA'].setup,
                                actuators=None,
                                muscle_force_path=trial.outputFiles['FORCES_SO'].abspath(),
                                results_directory=os.path.dirname(trial.outputFiles['JRA'].abspath()))

                ouput_files = trial.outputFiles['JRA'].abspath()
                utils.print_to_log(f'[success] Joint Reaction Analysis completed. Results are saved in {ouput_files}')

            except Exception as e:
                utils.print_to_log(f'Error during Joint Reaction Analysis: {e}')

        if False:
            run_jra.run_jra_setup(modelpath=trial.USED_MODEL,
                                setupJRA=trial.SETUP_JRA)

    # 8. Normalise EMG data
    if run['EMG_NORMALISE']:

        utils.print_to_log(f'Normalising EMG data for: {trial.subject} / {trial.name}')
        emg_normalise_list = []

        for name in paths.Settings().TRIAL_TO_ANALYSE:

            abs_path_emg = trial.inputFiles['EMG_MOT'].abspath()
            if os.path.exists(abs_path_emg):
                emg_normalise_list.append(abs_path_emg)
            else:
                print(f"EMG file not found: {abs_path_emg}")

        run_emg_normalise.main(target_emg_path=trial.inputFiles['EMG_MOT'].abspath(),
                    normalise_emg_list=emg_normalise_list)

        utils.print_to_log(f'EMG data normalised. Results are saved in {trial.inputFiles["EMG_MOT_NORMALISED"].abspath()}')

    # 9. Create excitation generator file
    if run['CREATE_EXCITATION_GENERATOR']:
        utils.print_to_log(f'Creating excitation generator file for: {trial.subject} / {trial.name}')
        try:
            #breakpoint()  # This will pause the execution for debugging
            save_path = trial.path + '\\' + 'excitationGenerator.xml'
            settings = paths.Settings()
            settings._create_excitation_generator(save_path=save_path,
                                                    replace=True)
            utils.print_to_log(f'Excitation generator file created successfully: {save_path}')

        except Exception as e:
            utils.print_to_log(f'Error creating excitation generator file: {e}')

    # 10. Run CEINMS calibration and optimization
    if run['CEINMS_CALIBRATION']:
        utils.print_to_log(f'Running CEINMS calibration on: {trial.subject} / {trial.name}')
        try:
            import run_ceinms_calibration
            run_ceinms_calibration.main(trial.CEINMS_SETUP_CALIBRATION)
            utils.print_to_log(f'CEINMS calibration completed successfully.')
        except Exception as e:
            print(f"Error during CEINMS calibration: {e}")
            utils.print_to_log(f'Error during CEINMS calibration: {e}')

    # 11. Run CEINMS optimization
    if run['CEINMS_OPTIMISATION']:
        utils.print_to_log(f'Running CEINMS optimization on: {trial.subject} / {trial.name}')
        try:
            import run_ceinms_optimisation
            run_ceinms_optimisation.main(trial.CEINMS_SETUP_OPTIMISATION)
            utils.print_to_log(f'CEINMS optimization completed successfully.')
        except Exception as e:
            print(f"Error during CEINMS optimization: {e}")
            utils.print_to_log(f'Error during CEINMS optimization: {e}')

def compare_trials(trial1: utils.Trial, trial2: utils.Trial):

    if True:
        try:
            trial1.compare_with(trial2)
        except Exception as e:
            print(f"Error during plotting: {e}")
            utils.print_to_log(f'Error during plotting: {e}')

def push_trial_results_to_git(trial: utils.Trial):
    """Push trial results to git after completion"""
    try:
        # Add all changes in the trial directory
        subprocess.run(['git', 'add', trial.path], check=True, cwd=os.getcwd())

        # Commit with descriptive message
        commit_message = f"[RESULT] {trial.subject}/{trial.name}"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True, cwd=os.getcwd())

        # Push to remote
        subprocess.run(['git', 'push'], check=True, cwd=os.getcwd())

        utils.print_to_log(f'[Success] Results pushed to git for: {trial.subject} / {trial.name}')

    except subprocess.CalledProcessError as e:
        utils.print_to_log(f'[Warning] Failed to push to git: {e}')
    except Exception as e:
        utils.print_to_log(f'[Warning] Git operation failed: {e}')

if __name__ == "__main__":
    utils.print_to_log("Starting analysis...")

    start_time = time.time()
    settings = utils.Settings()

    settings._print()

    answer = input("Do you want to proceed? (y/n): ")
    if answer.lower() != 'y':
        print("Exiting the program.")
        exit()

    analysis = utils.Analysis()

    trial_list = settings.TRIALS_TO_ANALYSE

    sessions_to_skip = ['25_03_31']
    subject_list = settings.SUBJECTS_TO_ANALYSE

    for subject in subject_list:

        session_list = analysis.get_subject(subject).SESSIONS

        for session in session_list:

            if session.name in sessions_to_skip: continue

            for trial in session.TRIALS:

                if trial.name not in trial_list: continue

                # trial.copy_inputs_to_trial(replace=False)

                utils.print_to_log(f'Running analysis for: {trial.subject} / {trial.name}')

                ##  Run main analysis function ##

                main(trial=trial, replace=True)

                #############################################

                utils.print_to_log(f'Analysis completed for: {trial.subject} / {trial.name}')

                # compare_trials(trial1=analysis.get_subject(subject).get_session(session.name).get_trial(trial_list[0]),
                #                  trial2=trial)

                # push results to git
                push_trial_results_to_git(trial=trial)

    end_time = time.time()
    elapsed_time = end_time - start_time
    utils.print_to_log(f"Total analysis time: {elapsed_time:.2f} seconds \n \n")

