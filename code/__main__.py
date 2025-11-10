import os
import subprocess
from xml.etree import ElementTree as ET
import time
import settings
import utils
import openSim
import ceinms
import exportC3D

def main(analyse: utils.Analyse, replace: bool = False):

    # Reset trials to only input files
    if settings.Execute().reset:
        analyse.reset()

    # create settings xml in trial folder
    if settings.Execute().create_settings_xml:
        analyse._to_xml()
    
    # Increase muscle force
    if settings.Execute().INCREASE_MUSCLE_FORCE: 
        scale_factor = settings.Execute().SCALE_FACTOR
        analyse.increase_muscle_force(factor=scale_factor, replace=replace)
        
    # Export c3d file
    if settings.Execute().exportC3D:
        subject_without_zero = analyse.subject.replace('0', '')
        exportC3D.export_markers(analyse.C3D,
                                strings_to_remove = ['Bar:', f'{subject_without_zero}:'])
        exportC3D.export_grf(analyse.C3D)
        exportC3D.export_emg(analyse.C3D)

    # Run IK
    if settings.Execute().IK:
        output_file = str(analyse.IK)
        try:
            if not os.path.exists(output_file) or replace:
                analyse.run_ik()
                utils.print_to_log(f'[Success] Inverse Kinematics completed. Results are saved in {output_file}')
            else:
                utils.print_to_log(f'[Info] Inverse Kinematics results already exist. Skipping computation. {output_file}')
        except Exception as e:
            utils.print_to_log(f'[Error] during Inverse Kinematics: {e}')

        try:
            virtual_marker_locations = analyse.path + '\\' + '_ik_model_marker_locations.sto'
            
            openSim.compare_marker_locations(marker_experimental_path=os.path.abspath(analyse.MARKERS),
                                          marker_virtual_path=virtual_marker_locations)
            utils.print_to_log(f'[Success] Marker location comparison completed.')
        except:
            utils.print_to_log(f'[Error] during marker location comparison')

    # Run ID
    if settings.Execute().ID:
        output_file = str(analyse.ID)
        try:

            # Check if the IK output file exists
            if not os.path.exists(output_file) or replace:
                analyse.run_id()
                utils.print_to_log(f'[Success] Inverse Dynamics completed. Results are saved in {output_file}')
            else:
                utils.print_to_log(f'[Info] Inverse Dynamics results already exist. Skipping computation. {output_file}')

        except Exception as e:
            utils.print_to_log(f'[Error] during Inverse Dynamics: {e}')

    # Run muscle analysis
    if settings.Execute().MA:
        try:
            if not os.path.exists(analyse.MA) or replace:
                analyse.run_ma()

                output_files = analyse.MA
                utils.print_to_log(f'[Success] Muscle Analysis completed. Results are saved in {output_files}')
        except Exception as e:
            utils.print_to_log(f'[Error] during Muscle Analysis: {e}')

    # Check moment arms
    if settings.Execute().MOMENT_ARMS:
        try:
            utils.checkMuscleMomentArms(osim_modelPath=analyse.modelPath,
                                        ik_output=analyse.IK,
                                        leg='l',
                                        threshold=0.005)

            utils.checkMuscleMomentArms(osim_modelPath=analyse.modelPath,
                                        ik_output=analyse.IK,
                                        leg='r',
                                        threshold=0.005)

            output_files = analyse.MA
            utils.print_to_log(f'[Success] Muscle moment arms checked. Results are saved in {output_files}')
        except Exception as e:
            utils.print_to_log(f'[Error] during Muscle moment arms check: {e}')

    # Run Static Optimization
    if settings.Execute().SO:

        try:
            # Check if the Static Optimization output file exists
            if not os.path.exists(analyse.SO_forces) or replace:
                analyse.run_so()
                utils.print_to_log(f'[Success] Static Optimization completed. Results are saved in {analyse.path}')

        except Exception as e:
            utils.print_to_log(f'[Error] during Static Optimization : {e}')

    # Run Joint Reaction Analysis
    if settings.Execute().JRA:
        try:
            analyse.run_jra()
            output_files = analyse.JRA
            utils.print_to_log(f'[success] Joint Reaction Analysis completed. Results are saved in {output_files}')

        except Exception as e:
            utils.print_to_log(f'Error during Joint Reaction Analysis: {e}')
    
    # Run Joint Reaction Analysis for CEINMS
    if settings.Execute().JRA_CEINMS:
        try:
            analyse.run_jra_ceinms()
            output_files = analyse.JRA_CEINMS
            utils.print_to_log(f'[success] Joint Reaction Analysis CEINMS completed. Results are saved in {output_files}')
        except Exception as e:
            utils.print_to_log(f'Error during Joint Reaction Analysis CEINMS: {e}')

    # Normalise EMG data
    if settings.Execute().EMG_NORMALISE:

        utils.print_to_log(f'Normalising EMG data for: {analyse.subject} / {analyse.name}')
        emg_normalise_list = []

        for name in settings.TRIALS_TO_ANALYSE:

            abs_path_emg = str(analyse.EMG_FILTERED)
            if os.path.exists(abs_path_emg):
                emg_normalise_list.append(abs_path_emg)
            else:
                print(f"EMG file not found: {abs_path_emg}")

        openSim.EMG_normalise(target_emg_path=str(analyse.EMG_FILTERED), 
                    normalise_emg_list=emg_normalise_list)

        utils.print_to_log(f'EMG data normalised. Results are saved in {analyse.EMG_NORMALISED}')

    if settings.Execute().SCALE_EMG:
        analyse.scale_emg(scale_factor=settings.Execute().EMG_SCALE_FACTOR,)
        
    # Create CEINMS setup files
    if settings.Execute().CREATE_CEINMS_FILES and (not os.path.exists(analyse.CEINMS_CALIBRATED_MODEL) or replace):
        
        # create CEINMS model file
        if settings.Execute().CREATE_CEINMS_MODEL and (not os.path.exists(analyse.CEINMS_UNCALIBRATED_MODEL)):
            try:
                analyse.create_ceinms_model()
            except Exception as e:
                utils.print_to_log(f'Error creating CEINMS model file: {e}')
        
        # create CEINMS input data XML file
        try:
            analyse.create_ceinms_input_data()
        except Exception as e:
            utils.print_to_log(f'Error creating CEINMS input data file: {e}')
        
        # create CEINMS calibration cfg XML file
        try:
            analyse.create_ceinms_calibration_gfc()
        except Exception as e:
            utils.print_to_log(f'Error creating CEINMS calibration cfg file: {e}')

        # create CEINMS excitation generator XML file
        try:
            analyse.create_excitation_generator()
        except Exception as e:
            utils.print_to_log(f'Error creating excitation generator file: {e}')
            
        # Create CEINMS calibration setup XML file
        try:       
            analyse.create_ceinms_calibration_setup()
        except Exception as e:
            utils.print_to_log(f'Error creating CEINMS calibration setup file: {e}')

        # Create CEINMS optimisation setup XML file
        try:       
            analyse.create_ceinms_optimise_setup()
        except Exception as e:
            utils.print_to_log(f'Error creating CEINMS optimisation setup file: {e}')
            
        # Create CEINMS optimisation cfg XML file
        try:       
            analyse.create_ceinms_optimise_cfg()
        except Exception as e:
            utils.print_to_log(f'Error creating CEINMS optimisation cfg file: {e}')    
        
    # CEINMS calibration and optimization
    if settings.Execute().CEINMS_CALIBRATION:
        
        try:        
            analyse.run_ceinms_calibration()
        
        except Exception as e:
            print(f"Error during CEINMS calibration: {e}")
            utils.print_to_log(f'Error during CEINMS calibration: {e}')

    # CEINMS optimisation
    if settings.Execute().CEINMS_OPTIMISATION:
        try:
            analyse.run_ceinms_optimise()
        except Exception as e:
            utils.print_to_log(f'Error during CEINMS optimisation: {e}')

    if settings.Execute().CEINMS_EXE:
        try:
           analyse.run_ceinms_exe()
        except Exception as e:
            utils.print_to_log(f'Error during CEINMS executable run: {e}')

    if settings.Execute().CREATE_PLOTS:
        try:
            if settings.Execute().PLOT_IK: analyse.plot_ik()
            if settings.Execute().PLOT_ID: analyse.plot_id()
            if settings.Execute().PLOT_MA: analyse.plot_ma()
            if settings.Execute().PLOT_SO: analyse.plot_so()
            if settings.Execute().PLOT_JRA: analyse.plot_jra()
            if settings.Execute().PLOT_EMG: analyse.plot_emg()

            utils.print_to_log(f'Plots created successfully for: {analyse.subject} / {analyse.name}')
        except Exception as e:
            print(f"Error during plotting: {e}")
            utils.print_to_log(f'Error during plotting: {e}')
             
def compare_trials(trial1: utils.Analyse, trial2: utils.Analyse):

    if True:
        try:
            trial1.compare_with(trial2)
        except Exception as e:
            print(f"Error during plotting: {e}")
            utils.print_to_log(f'Error during plotting: {e}')

def push_trial_results_to_git(trial: utils.Analyse):
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
    time.sleep(1)

    for subject in settings.SUBJECTS_TO_ANALYSE:
        for session in settings.SESSIONS_TO_ANALYSE:
            trial_list = os.listdir(os.path.join(settings.SIMULATIONS_DIR,
                                                 subject,
                                                 session))
            for trial_name in trial_list:
                
                if trial_name not in settings.TRIALS_TO_ANALYSE:
                    continue
                
                trialPath = os.path.join(settings.SIMULATIONS_DIR,
                                         subject,
                                         session,
                                         trial_name)
                
                trial = utils.Analyse(trialPath=trialPath) 
                
                utils.print_to_log(f'Running analysis for: {trial.subject} / {trial.name}')

                ##  Run main analysis function ##

                main(analyse=trial, replace=False)

                #############################################

                utils.print_to_log(f'Analysis completed for: {trial.subject} / {trial.name}')

                if settings.Execute().push_to_git:
                    push_trial_results_to_git(trial=trial)

    end_time = time.time()
    elapsed_time = end_time - start_time
    utils.print_to_log(f"Total analysis time: {elapsed_time:.2f} seconds \n \n")

