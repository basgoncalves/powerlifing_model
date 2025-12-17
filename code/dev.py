import os
import subprocess
from xml.etree import ElementTree as ET
import time
import utils
from utils import load_any_data_file
import matplotlib.pyplot as plt
import openSim
import ceinms
import exportC3D

subjectLiist = ['Athlete_03_MRI_Katya'] #Athlete_03_MRI_BG
session = '25_03_31'
trial = 'Walking_03'  # 'Walking_02', 'Squat_35kg_01', 'Squat_bw_01'

for subject in subjectLiist:
                
        trialPath = os.path.join(utils.SIMULATIONS_DIR, subject, session, trial)
        print(f'Analyzing trial at path: {trialPath}')
        analysis = utils.Analyse(trialPath)
      

        #%% Load settings
        if False:  analysis.reset_settings_xml()

        # print main inputs
        print("Main inputs:")
        print(f"Model file: {analysis.model_dir}")
        print(f"time range: {analysis.time_range}")
        print(f"IK file: {analysis.ik}")

        new_model = os.path.join(utils.MODELS_DIR, subject, session, 'scaled_increased_3.00.osim')
        analysis.update_model(new_model)
        if True: analysis.run_ik()
        if True: analysis.run_id()
        if True:  analysis.run_ma()
        if True:  analysis.run_so()

        if True:  analysis.run_emg_normalise()
        if True:  analysis.scale_emg(scale_factor=0.70)

        #%% CEINMS setups
        if False:  analysis.create_ceinms_model()
        if True:  analysis.create_ceinms_input_data()

        if False:  analysis.create_ceinms_calibration_cfg(calibration_trial_names=['Walking_02'])

        if False:  analysis.create_ceinms_calibration_setup()

        if False:  analysis.create_excitation_generator()


        #%% CEINMS calibration and optimization
        if False:  analysis.run_ceinms_calibration()
        if False:  ceinms.plot_ceinms_model_parameters(os.path.join(analysis.path, '..\subjectCalibrated.xml'))
        if False:  ceinms.plot_ceinms_calibration_results(setupXML_path=analysis.ceinms_calibration_setup)
        if False:  ceinms.plot_compare_ceinms_models(analysis.ceinms_uncalibrated_model, analysis.ceinms_calibrated_model)

        if True:  analysis.create_ceinms_exe_cfg()

        if True:  analysis.create_ceinms_exe_setup()

        if False:  analysis.run_ceinms_exe_loop()
        if True:  analysis.run_ceinms_exe()
        if False:  analysis.create_ceinms_optimise_setup()
        if False:  analysis.run_ceinms_optimise()

        analysis.update_trial_attribute('jra_forces_ceinms', 'Execution_a10_b1_g1000\MuscleForces.sto')
        analysis.load_settings(analysis.settingsXML)

        if True:      
                analysis.replace = True
                new_model = os.path.join(utils.MODELS_DIR, subject, session, 'scaled.osim')
                analysis.update_model(new_model)
                analysis.run_jra_ceinms()

        if True:
                analysis.replace = True
                new_model = os.path.join(utils.MODELS_DIR, subject, session, 'scaled_increased_3.00.osim')
                analysis.update_model(new_model)
                analysis.run_jra()

        if True: analysis.push_trial_results_to_git()

        

