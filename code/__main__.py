import os
import subprocess
from xml.etree import ElementTree as ET
import time
import settings
import utils
import run_ik, run_id, run_so, run_ma, run_jra
import run_emg_normalise
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
        scale_factor = settings.Execute().SCALE_FACTOR
        trial.increase_muscle_force(factor=scale_factor, replace=replace)
        
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
                trial.run_ik()
                utils.print_to_log(f'[Success] Inverse Kinematics completed. Results are saved in {output_file}')
            else:
                utils.print_to_log(f'[Info] Inverse Kinematics results already exist. Skipping computation. {output_file}')
        except Exception as e:
            utils.print_to_log(f'[Error] during Inverse Kinematics: {e}')

        try:
            virtual_marker_locations = trial.path + '\\' + '_ik_model_marker_locations.sto'
            compare_marker_locations.main(marker_experimental_path=os.path.abspath(trial.inputFiles.MARKERS),
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
                trial.run_id()
                utils.print_to_log(f'[Success] Inverse Dynamics completed. Results are saved in {output_file}')
            else:
                utils.print_to_log(f'[Info] Inverse Dynamics results already exist. Skipping computation. {output_file}')

        except Exception as e:
            utils.print_to_log(f'[Error] during Inverse Dynamics: {e}')

    # Run muscle analysis
    if settings.Execute().MA:

        try:
            if not os.path.exists(trial.outputFiles.MA) or replace:
                trial.run_ma()

                output_files = trial.outputFiles.MA
                utils.print_to_log(f'[Success] Muscle Analysis completed. Results are saved in {output_files}')
        except Exception as e:
            utils.print_to_log(f'[Error] during Muscle Analysis: {e}')

    # Check moment arms
    if settings.Execute().MOMENT_ARMS:
        try:
            utils.checkMuscleMomentArms(osim_modelPath=trial.modelPath,
                                        ik_output=trial.outputFiles.IK,
                                        leg='l',
                                        threshold=0.005)

            utils.checkMuscleMomentArms(osim_modelPath=trial.modelPath,
                                        ik_output=trial.outputFiles.IK,
                                        leg='r',
                                        threshold=0.005)

            output_files = trial.outputFiles.MA
            utils.print_to_log(f'[Success] Muscle moment arms checked. Results are saved in {output_files}')
        except Exception as e:
            utils.print_to_log(f'[Error] during Muscle moment arms check: {e}')

    # Run Static Optimization
    if settings.Execute().SO:

        try:
            # Check if the Static Optimization output file exists
            if not os.path.exists(trial.outputFiles.SO_forces) or replace:
                trial.run_so()
                utils.print_to_log(f'[Success] Static Optimization completed. Results are saved in {trial.outputFiles["SO"].abspath()}')

        except Exception as e:
            utils.print_to_log(f'[Error] during Static Optimization : {e}')

    # Run Joint Reaction Analysis
    if settings.Execute().JRA:
        try:
            trial.run_jra()
            output_files = trial.outputFiles.JRA
            utils.print_to_log(f'[success] Joint Reaction Analysis completed. Results are saved in {output_files}')

        except Exception as e:
            utils.print_to_log(f'Error during Joint Reaction Analysis: {e}')

    # Normalise EMG data
    if settings.Execute().EMG_NORMALISE:

        utils.print_to_log(f'Normalising EMG data for: {trial.subject} / {trial.name}')
        emg_normalise_list = []

        for name in settings.TRIALS_TO_ANALYSE:

            abs_path_emg = str(trial.inputFiles.EMG_FILTERED)
            if os.path.exists(abs_path_emg):
                emg_normalise_list.append(abs_path_emg)
            else:
                print(f"EMG file not found: {abs_path_emg}")

        run_emg_normalise.main(target_emg_path=str(trial.inputFiles.EMG_FILTERED),
                    normalise_emg_list=emg_normalise_list)

        utils.print_to_log(f'EMG data normalised. Results are saved in {trial.inputFiles.EMG_NORMALISED}')

    # Create CEINMS setup files
    if settings.Execute().CREATE_CEINMS_FILES and (not os.path.exists(trial.inputFiles.CEINMS_CALIBRATED_MODEL) or replace):
        
        # create CEINMS model file
        if settings.Execute().CREATE_CEINMS_MODEL and (not os.path.exists(trial.inputFiles.CEINMS_UNCALIBRATED_MODEL)):
            try:
                trial.create_ceinms_model()
            except Exception as e:
                utils.print_to_log(f'Error creating CEINMS model file: {e}')
            
        # create CEINMS input data XML file
        try:
            trial.create_ceinms_input_data()
        except Exception as e:
            utils.print_to_log(f'Error creating CEINMS input data file: {e}')
        
        # create CEINMS calibration cfg XML file
        try:
            trial.create_ceinms_calibration_gfc()
        except Exception as e:
            utils.print_to_log(f'Error creating CEINMS calibration cfg file: {e}')

        # create CEINMS excitation generator XML file
        try:
            trial.create_excitation_generator()
        except Exception as e:
            utils.print_to_log(f'Error creating excitation generator file: {e}')
            
        # Create CEINMS calibration setup XML file
        try:       
            trial.create_ceinms_calibration_setup()
        except Exception as e:
            utils.print_to_log(f'Error creating CEINMS calibration setup file: {e}')

        # Create CEINMS optimisation setup XML file
        try:       
            trial.create_ceinms_optimise_setup()
        except Exception as e:
            utils.print_to_log(f'Error creating CEINMS optimisation setup file: {e}')
            
        # Create CEINMS optimisation cfg XML file
        try:       
            trial.create_ceinms_optimise_cfg()
        except Exception as e:
            utils.print_to_log(f'Error creating CEINMS optimisation cfg file: {e}')    
        
    # CEINMS calibration and optimization
    if settings.Execute().CEINMS_CALIBRATION:
        
        try:
            start_time = time.time()
            ceinms.plot_ceinms_model_parameters(trial.inputFiles.CEINMS_UNCALIBRATED_MODEL)
            trial.run_ceinms_calibration()
            
            # if date modified of calibrated model is after start time, assume success
            mod_time = os.path.getmtime(trial.inputFiles.CEINMS_CALIBRATED_MODEL)
            if mod_time >= start_time:
                utils.print_to_log(f'CEINMS calibration completed successfully in {end_time - start_time:.2f} seconds.')
                ceinms.plot_ceinms_model_parameters(trial.inputFiles.CEINMS_CALIBRATED_MODEL)
            else:
                utils.print_to_log(f'CEINMS calibration may have failed: calibrated model not updated.')
                
        except Exception as e:
            print(f"Error during CEINMS calibration: {e}")
            utils.print_to_log(f'Error during CEINMS calibration: {e}')

    # CEINMS optimisation
    if settings.Execute().CEINMS_OPTIMISATION:
        try:
            ceinms.optimise(setupXML_path=trial.inputFiles.CEINMS_OPTIMISE_SETUP)

            adjustedEMG_path = os.path.join(trial.outputFiles.CEINMS_OPTIMISATION_DIR, 'adjustedEMG.sto')
            ceinms.plot_emg_vs_ceimns(emgFile=trial.inputFiles.EMG_NORMALISED,
                                      ceinmsExcitationsFile=adjustedEMG_path)
            
            torqueCEINMS_path = os.path.join(trial.outputFiles.CEINMS_OPTIMISATION_DIR, 'Torques.sto')
            ceinms.plot_moments_vs_ceinms(externalMomentsFile=trial.outputFiles.ID,
                                          ceinmsMomentsFile=torqueCEINMS_path)
        except Exception as e:
            utils.print_to_log(f'Error during CEINMS optimisation: {e}')

    if settings.Execute().CREATE_PLOTS:
        try:
            trial.plot_ik()
            trial.plot_id()
            trial.plot_so()
            trial.plot_jra()
            trial.plot_emg()
            
            utils.print_to_log(f'Plots created successfully for: {trial.subject} / {trial.name}')
        except Exception as e:
            print(f"Error during plotting: {e}")
            utils.print_to_log(f'Error during plotting: {e}')
             
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
    
    print(f'Check settings in {settings.__file__}')

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

