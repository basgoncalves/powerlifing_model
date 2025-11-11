import os
import subprocess
from xml.etree import ElementTree as ET
import time
import settings
import utils
import openSim
import ceinms
import exportC3D

def main(analyse: utils.Analyse):
    
    # Increase muscle force
    if settings.Execute().INCREASE_MUSCLE_FORCE: 
        scale_factor = settings.Execute().SCALE_FACTOR
        analyse.increase_muscle_force(factor=scale_factor, replace=True)
        
    # Export c3d file
    if settings.Execute().exportC3D:
        subject_without_zero = analyse.subject.replace('0', '')
        exportC3D.export_markers(analyse.C3D,
                                strings_to_remove = ['Bar:', f'{subject_without_zero}:'])
        exportC3D.export_grf(analyse.C3D)
        exportC3D.export_emg(analyse.C3D)

    # Run IK
    if settings.Execute().IK:
        analyse.run_ik()
        analyse.compare_marker_locations()

    # Run ID
    if settings.Execute().ID: 
        analyse.run_id()

    # Run muscle analysis
    if settings.Execute().MA: 
        analyse.run_ma()

    # Check moment arms
    if settings.Execute().MOMENT_ARMS:
        try:
            utils.checkMuscleMomentArms(osim_modelPath=analyse.MODEL,
                                        ik_output=analyse.IK,
                                        leg='l',
                                        threshold=0.005)

            utils.checkMuscleMomentArms(osim_modelPath=analyse.MODEL,
                                        ik_output=analyse.IK,
                                        leg='r',
                                        threshold=0.005)

            output_files = analyse.MA
            utils.print_to_log(f'[Success] Muscle moment arms checked. Results are saved in {output_files}')
        except Exception as e:
            utils.print_to_log(f'[Error] during Muscle moment arms check: {e}')

    # Run Static Optimization
    if settings.Execute().SO:
        analyse.run_so()

    # Run Joint Reaction Analysis
    if settings.Execute().JRA:
        analyse.run_jra()
        
    # Normalise EMG data
    if settings.Execute().EMG_NORMALISE:

        utils.print_to_log(f'Normalising EMG data for: {analyse.subject} / {analyse.trial}')
        emg_normalise_list = []

        for name in settings.TRIALS_TO_ANALYSE:

            abs_path_emg = str(analyse.EMG_FILTERED)
            if os.path.exists(abs_path_emg):
                emg_normalise_list.append(abs_path_emg)
            else:
                print(f"EMG file not found: {abs_path_emg}")

        openSim.run_emg_normalise(target_emg_path=str(analyse.EMG_FILTERED), 
                    normalise_emg_list=emg_normalise_list)

        utils.print_to_log(f'EMG data normalised. Results are saved in {analyse.EMG_NORMALISED}')

    if settings.Execute().SCALE_EMG:
        analyse.scale_emg(scale_factor=settings.Execute().EMG_SCALE_FACTOR)
        
    # Create CEINMS setup files
    if settings.Execute().CREATE_CEINMS_FILES:
        
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
                
        
    # CEINMS calibration and optimization
    if settings.Execute().CEINMS_CALIBRATION and analyse.trial in settings.CEINMS_CALIBRATION_TRIALS:
        
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

        # Run Joint Reaction Analysis for CEINMS
    
    # Run Joint Reaction Analysis with CEINMS muscle forces
    if settings.Execute().JRA_CEINMS:
        analyse.run_jra_ceinms()
    
    if settings.Execute().CREATE_PLOTS:
        try:
            if settings.Execute().PLOT_IK: analyse.plot_ik()
            if settings.Execute().PLOT_ID: analyse.plot_id()
            if settings.Execute().PLOT_MA: analyse.plot_ma()
            if settings.Execute().PLOT_SO: analyse.plot_so()
            if settings.Execute().PLOT_JRA: analyse.plot_jra()
            if settings.Execute().PLOT_EMG: analyse.plot_emg()

            utils.print_to_log(f'Plots created successfully for: {analyse.subject} / {analyse.trial}')
        except Exception as e:
            print(f"Error during plotting: {e}")
            utils.print_to_log(f'Error during plotting: {e}')
             
def push_trial_results_to_git(trial: utils.Analyse):
    """Push trial results to git after completion"""
    try:
        # Add all changes in the trial directory
        subprocess.run(['git', 'add', trial.path], check=True, cwd=os.getcwd())

        # Commit with descriptive message
        commit_message = f"[RESULT] {trial.subject}/{trial.trial}"
        subprocess.run(['git', 'commit', '-m', commit_message], check=True, cwd=os.getcwd())

        # Push to remote
        subprocess.run(['git', 'push'], check=True, cwd=os.getcwd())

        utils.print_to_log(f'[Success] Results pushed to git for: {trial.subject} / {trial.trial}')

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
                
                analysis = utils.Analyse(trialPath=trialPath) 
                
                utils.print_to_log(f'Running analysis for: {trialPath}')

                ##  Run main analysis function ##
                main(analyse=analysis)

                #############################################

                utils.print_to_log(f'Analysis completed for: {trialPath}')

                if settings.Execute().push_to_git:
                    push_trial_results_to_git(trial=analysis)

    end_time = time.time()
    elapsed_time = end_time - start_time
    utils.print_to_log(f"Total analysis time: {elapsed_time:.2f} seconds \n \n")

