import os
import subprocess
from xml.etree import ElementTree as ET
import time
import settings
import utils
import run_ik, run_id, run_so, run_ma, run_jra
import run_emg_normalise
import run_ceinms_optimise
import ceinms
import exportC3D, compare_marker_locations, calculate_muscle_moments

def main(trial: utils.Trial, replace: bool = False):

    # Reset trials to only input files
    if settings.Execute().reset:
        trial.reset()

    # create settings xml in trial folder
    if settings.Execute().create_settings_xml:
        trial._to_xml()
    
    # Increase muscle force
    if settings.Execute().INCREASE_MUSCLE_FORCE:
        trial.increase_muscle_force(factor=3, replace=replace)

    # Export c3d file
    if settings.Execute().exportC3D:
        subject_without_zero = trial.subject.replace('0', '')
        exportC3D.export_markers(trial.inputFiles['C3D'].abspath(),
                                strings_to_remove = ['Bar:', f'{subject_without_zero}:'])
        exportC3D.export_grf(trial.inputFiles['C3D'].abspath())
        exportC3D.export_emg(trial.inputFiles['C3D'].abspath())

    # Run IK
    if settings.Execute().IK:
        output_file = str(trial.outputFiles.IK)
        try:

            if not os.path.exists(output_file) or replace:
                os.chdir(trial.path)

                run_ik.main(osim_modelPath=settings.Inputs().osimModel,
                            marker_trc=settings.Inputs().MARKERS,
                            ik_output=output_file,
                            setup_xml=settings.SetupFiles().IK,
                            time_range=trial.get_time_range(),
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

    # Run ID
    if settings.Execute().ID:
        output_file = str(trial.outputFiles.ID)
        try:

            # Check if the IK output file exists
            if not os.path.exists(output_file) or replace:
                os.chdir(trial.path)
                run_id.main(osimModelPath=settings.Inputs().osimModel,
                            ikOutputPath=settings.Outputs().IK,
                            grfXmlPath=settings.Inputs().GRF,
                            setupXmlPath=settings.SetupFiles().ID,
                            resultsDir=trial.path)

                utils.print_to_log(f'[Success] Inverse Dynamics completed. Results are saved in {output_file}')
            else:
                utils.print_to_log(f'[Info] Inverse Dynamics results already exist. Skipping computation. {output_file}')

        except Exception as e:
            utils.print_to_log(f'[Error] during Inverse Dynamics: {e}')
            exit()

    # Run muscle analysis
    if settings.Execute().MA:

        try:
            if not os.path.exists(trial.outputFiles.MA) or replace:
                run_ma.main(osim_modelPath=trial.inputFiles.osimModel,
                            ik_output=trial.outputFiles.IK,
                            grf_xml=trial.setupFiles.GRF,
                            setup_xml=trial.setupFiles.MA,
                            resultsDir=trial.outputFiles.MA)

                output_files = trial.outputFiles.MA
                utils.print_to_log(f'[Success] Muscle Analysis completed. Results are saved in {output_files}')
        except Exception as e:
            utils.print_to_log(f'[Error] during Muscle Analysis: {e}')
            exit()

    # Check moment arms
    if settings.Execute().MOMENT_ARMS:
        try:
            utils.checkMuscleMomentArms(osim_modelPath=str(trial.inputFiles.osimModel),
                                        ik_output=str(trial.outputFiles.IK),
                                        leg='l',
                                        threshold=0.005)

            utils.checkMuscleMomentArms(osim_modelPath=str(trial.inputFiles.osimModel),
                                        ik_output=str(trial.outputFiles.IK),
                                        leg='r',
                                        threshold=0.005)

            output_files = str(trial.outputFiles.MA)
            utils.print_to_log(f'[Success] Muscle moment arms checked. Results are saved in {output_files}')
        except Exception as e:
            utils.print_to_log(f'[Error] during Muscle moment arms check: {e}')

    # Run Static Optimization
    if settings.Execute().SO:

        try:
            # Check if the Static Optimization output file exists
            if not os.path.exists(str(trial.outputFiles.SO)) or replace:

                run_so.main(osim_modelPath=str(trial.inputFiles.osimModel),
                            ik_output=str(trial.outputFiles.IK),
                            grf_xml=str(trial.setupFiles.GRF),  
                            setup_xml=str(trial.setupFiles.SO),
                            actuators=str(trial.inputFiles.ACTUATORS_SO),
                            resultsDir=trial.outputFiles.SO)

                utils.print_to_log(f'[Success] Static Optimization completed. Results are saved in {trial.outputFiles["SO"].abspath()}')

        except Exception as e:
            utils.print_to_log(f'[Error] during Static Optimization : {e}')

    # Run Joint Reaction Analysis
    if settings.Execute().JRA:
        if True:
            try:
                
                run_jra.main(modelpath=str(trial.inputFiles.osimModel),
                             coordinates_file=str(trial.outputFiles.IK),
                             externalloadsfile=str(trial.setupFiles.GRF),
                             setupJRA=str(trial.setupFiles.JRA),
                             actuators=None,
                             muscle_force_path=str(trial.outputFiles['FORCES_SO'].abspath()),
                             results_directory=os.path.dirname(trial.outputFiles['JRA'].abspath()))

                ouput_files = trial.outputFiles['JRA'].abspath()
                utils.print_to_log(f'[success] Joint Reaction Analysis completed. Results are saved in {ouput_files}')

            except Exception as e:
                utils.print_to_log(f'Error during Joint Reaction Analysis: {e}')

        if False:
            run_jra.run_jra_setup(modelpath=trial.USED_MODEL,
                                setupJRA=trial.SETUP_JRA)

    # Normalise EMG data
    if settings.Execute().EMG_NORMALISE:

        utils.print_to_log(f'Normalising EMG data for: {trial.subject} / {trial.name}')
        emg_normalise_list = []

        for name in settings.TRIAL_TO_ANALYSE:

            abs_path_emg = str(trial.inputFiles.EMG_FILTERED)
            if os.path.exists(abs_path_emg):
                emg_normalise_list.append(abs_path_emg)
            else:
                print(f"EMG file not found: {abs_path_emg}")

        run_emg_normalise.main(target_emg_path=str(trial.inputFiles.EMG_FILTERED),
                    normalise_emg_list=emg_normalise_list)

        utils.print_to_log(f'EMG data normalised. Results are saved in {trial.inputFiles["EMG_MOT_NORMALISED"].abspath()}')

    # Create CEINMS setup files
    if settings.Execute().CREATE_CEINMS_FILES and (not os.path.exists(trial.inputFiles.CEINMS_CALIBRATED_MODEL) or replace):
        
        # create CEINMS model file
        try:
            ceinms.create_ceinms_model(osimModelPath=trial.modelPath,
                                       savePath=trial.setupFiles.CEINMS_UNCALIBRATED_MODEL)

            utils.print_to_log(f'CEINMS model file created successfully: {trial.setupFiles.CEINMS_UNCALIBRATED_MODEL}')
        except Exception as e:
            utils.print_to_log(f'Error creating CEINMS model file: {e}')
        
        # create CEINMS input data XML file
        try:
            trial.create_ceinms_input_data()
        except Exception as e:
            utils.print_to_log(f'Error creating CEINMS input data file: {e}')
          
        # create CEINMS calibration cfg XML file
        try:
            input_paths = []
            for trial in settings.CEINMSParameters().calibration_trials:
                input_paths.append(trial + os.path.sep + settings.Inputs().CEINMS_INPUT_DATA)
            
            ceinms.create_calibrationCfg(osimModelPath=trial.modelPath,
                                        inputPaths=input_paths,
                                        outputPath=trial.inputFiles.CEINMS_CALIBRATION_CFG)
            
            utils.print_to_log(f'CEINMS calibration cfg file created successfully: {save_path}')
        except Exception as e:
            utils.print_to_log(f'Error creating CEINMS calibration cfg file: {e}')

        # create CEINMS excitation generator XML file
        try:
            save_path = os.path.join(os.path.dirname(trial.path), settings.Inputs().CEINMS_EXCITATION_GENERATOR)
            
            ceinms.create_excitation_mapping(
                osim_model_path=trial.modelPath,
                emg_path=trial.inputFiles.CEINMS_EXCITATIONS,
                save_path=save_path
            )
            utils.print_to_log(f'Excitation generator file created successfully: {save_path}')
        except Exception as e:
            utils.print_to_log(f'Error creating excitation generator file: {e}')
            
        # Create CEINMS calibration setup XML file
        try:       
            trial.create_ceinms_calibration_setup()
            utils.print_to_log(f'CEINMS calibration setup file created successfully: {trial.path}')
        except Exception as e:
            utils.print_to_log(f'Error creating CEINMS calibration setup file: {e}')

           
    # CEINMS calibration and optimization
    if settings.Execute().CEINMS_CALIBRATION:
        utils.print_to_log(f'Running CEINMS calibration on: {trial.subject} / {trial.name}')
        try:
            ceinms.calibrate(setupXML_path=trial.setupFiles.CEINMS_CALIBRATION_SETUP)
        except Exception as e:
            print(f"Error during CEINMS calibration: {e}")
            utils.print_to_log(f'Error during CEINMS calibration: {e}')

    # CEINMS optimization
    if settings.Execute().CEINMS_OPTIMISATION:
        utils.print_to_log(f'Running CEINMS optimization on: {trial.subject} / {trial.name}')
        try:
            run_ceinms_optimise.main(trial.inputFiles['CEINMS_OPTIMISE_SETUP'].abspath())
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
    settings._print()

    answer = input("Do you want to proceed? (y/n): ")
    if answer.lower() != 'y':
        print("Exiting the program.")
        exit()

    for subject in settings.SUBJECTS_TO_ANALYSE:
        for session in settings.SESSIONS_TO_ANALYSE:
            for trial_name in settings.TRIALS_TO_ANALYSE:
                
                trial = utils.Trial(subject_name=subject, 
                                    session_name=session, 
                                    trial_name=trial_name) 

                utils.print_to_log(f'Running analysis for: {trial.subject} / {trial.name}')

                ##  Run main analysis function ##

                main(trial=trial, replace=True)

                #############################################

                utils.print_to_log(f'Analysis completed for: {trial.subject} / {trial.name}')

                # compare_trials(trial1=analysis.get_subject(subject).get_session(session.name).get_trial(trial_list[0]),
                #                  trial2=trial)

                if settings.Execute().push_to_git:
                    push_trial_results_to_git(trial=trial)

    end_time = time.time()
    elapsed_time = end_time - start_time
    utils.print_to_log(f"Total analysis time: {elapsed_time:.2f} seconds \n \n")

