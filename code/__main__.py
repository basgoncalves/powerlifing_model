import os
import subprocess
from xml.etree import ElementTree as ET
import time
import settings
import utils
import openSim
import ceinms
import exportC3D

SUBJECTS_TO_ANALYSE =  ['Athlete_03'] 
SESSIONS_TO_ANALYSE = ['25_03_31'] 
TRIALS_TO_ANALYSE =  ['Walking_03'] 
CEINMS_CALIBRATION_TRIALS = ['Walking_02'] 

class Execute:
    ''' Logics for which analyses to execute '''
    def __init__(self):
        
        self.replace = False

        self.INCREASE_MUSCLE_FORCE = False
        self.SCALE_FACTOR = 3
        self.exportC3D = False
        self.IK = False
        self.ID = False
        self.MA = False
        self.MOMENT_ARMS = False
        self.SO = False
        self.JRA = True
        
        self.EMG_NORMALISE = False
        self.SCALE_EMG = False
        self.EMG_SCALE_FACTOR = 0.7
        
        self.CREATE_CEINMS_FILES = False
        self.CREATE_CEINMS_MODEL = False
        
        self.CEINMS_CALIBRATION = False
        self.CEINMS_CALIBRATION_PLOTS = False
        
        self.CEINMS_OPTIMISATION = False
        self.CEINMS_EXE = False
        self.CEINMS_EXE_LOOP = False
        
        self.JRA_CEINMS = False
        
        self.CREATE_PLOTS = False
        
        self.PLOT_IK = False
        self.PLOT_ID = False
        self.PLOT_MA = False
        self.PLOT_SO = False
        self.PLOT_JRA = False
        self.PLOT_EMG = False
          
        self.push_to_git = True

def run_all_step(analyse: utils.Analyse):
    
    # Export c3d file
    if Execute().exportC3D:
        subject_without_zero = analyse.subject.replace('0', '')
        exportC3D.export_markers(analyse.c3d,
                                strings_to_remove = ['Bar:', f'{subject_without_zero}:'])
        exportC3D.export_grf(analyse.c3d)
        exportC3D.export_emg(analyse.c3d)

    # Run IK
    if Execute().IK:
        analyse.run_ik()
        analyse.compare_marker_locations()

    # Run ID
    if Execute().ID: 
        analyse.run_id()

    # Run muscle analysis
    if Execute().MA: 
        analyse.run_ma()

    # Check moment arms
    if Execute().MOMENT_ARMS:
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
    if Execute().SO:
        analyse.run_so()

    # Run Joint Reaction Analysis
    if Execute().JRA:
        analyse.update_trial_attribute('jra', 'Analyse_JRA_ReactionLoads_SO.sto')
        analyse.run_jra()
        
    # Normalise EMG data
    if Execute().EMG_NORMALISE:

        utils.print_to_log(f'Normalising EMG data for: {analyse.subject} / {analyse.trial}')
        emg_normalise_list = []

        for name in TRIALS_TO_ANALYSE:

            abs_path_emg = str(analyse.emg_filtered)
            if os.path.exists(abs_path_emg):
                emg_normalise_list.append(abs_path_emg)
            else:
                print(f"EMG file not found: {abs_path_emg}")

        openSim.run_emg_normalise(target_emg_path=str(analyse.emg_filtered), 
                    normalise_emg_list=emg_normalise_list)

        utils.print_to_log(f'EMG data normalised. Results are saved in {analyse.emg_normalised}')

    if Execute().SCALE_EMG:
        analyse.scale_emg(scale_factor=settings.Execute().EMG_SCALE_FACTOR)
        
    # Create CEINMS setup files
    if Execute().CREATE_CEINMS_FILES:
        
        # create CEINMS model file
        if settings.Execute().CREATE_CEINMS_MODEL and (not os.path.exists(analyse.ceinms_uncalibrated_model) or analyse.replace):
            try:
                analyse.create_ceinms_model()
            except Exception as e:
                utils.print_to_log(f'Error creating CEINMS model file: {e}')
        
        analyse.replace = False

        analyse.create_ceinms_model()

        analyse.create_ceinms_input_data()
        
        analyse.create_ceinms_calibration_cfg()

        analyse.create_ceinms_calibration_setup()

        analyse.create_excitation_generator()

        analyse.create_ceinms_exe_cfg()

        analyse.create_ceinms_exe_setup()
                
    # CEINMS calibration and optimization
    if Execute().CEINMS_CALIBRATION and analyse.trial in CEINMS_CALIBRATION_TRIALS:
        
        try:        
            analyse.run_ceinms_calibration()
        
        except Exception as e:
            print(f"Error during CEINMS calibration: {e}")
            utils.print_to_log(f'Error during CEINMS calibration: {e}')

    # CEINMS optimisation
    if Execute().CEINMS_OPTIMISATION:
        try:
            analyse.run_ceinms_optimise()
        except Exception as e:
            utils.print_to_log(f'Error during CEINMS optimisation: {e}')

    if Execute().CEINMS_EXE:
        try:
           analyse.run_ceinms_exe()
        except Exception as e:
            utils.print_to_log(f'Error during CEINMS executable run: {e}')

        # Run Joint Reaction Analysis for CEINMS
    
    if Execute().CEINMS_EXE_LOOP:
        try:
            analyse.run_ceinms_exe_loop()
        except Exception as e:
            utils.print_to_log(f'Error during CEINMS executable loop run: {e}')
    
    # Run Joint Reaction Analysis with CEINMS muscle forces
    if Execute().JRA_CEINMS:
        analyse.run_jra_ceinms()
    
    if Execute().CREATE_PLOTS:
        try:
            if Execute().PLOT_IK: analyse.plot_ik()
            if Execute().PLOT_ID: analyse.plot_id()
            if Execute().PLOT_SO: analyse.plot_so()
            if Execute().PLOT_JRA: analyse.plot_jra()
            

            utils.print_to_log(f'Plots created successfully for: {analyse.subject} / {analyse.trial}')
        except Exception as e:
            print(f"Error during plotting: {e}")
            utils.print_to_log(f'Error during plotting: {e}')
             
if __name__ == "__main__":
    utils.print_to_log("Starting analysis...")

    start_time = time.time()
    
    print(f'Check settings in {settings.__file__}')
    time.sleep(1)
    for subject in SUBJECTS_TO_ANALYSE:
        for session in SESSIONS_TO_ANALYSE:

            trial_list = os.listdir(os.path.join(utils.SIMULATIONS_DIR, subject,session))

            for trial_name in trial_list:
                
                if trial_name not in TRIALS_TO_ANALYSE: continue
                
                trialPath = os.path.join(utils.SIMULATIONS_DIR, subject, session, trial_name)
                
                analysis = utils.Analyse(trialPath=trialPath) 
                
                utils.print_to_log(f'Running analysis for: {trialPath}')

                ##  Run main analysis function ##
                run_all_step(analyse=analysis)

                #############################################

                utils.print_to_log(f'Analysis completed for: {trialPath}')

                
                if Execute().push_to_git:
                    analysis.push_trial_results_to_git()

        
    
    end_time = time.time()
    elapsed_time = end_time - start_time
    utils.print_to_log(f"Total analysis time: {elapsed_time:.2f} seconds \n \n")

