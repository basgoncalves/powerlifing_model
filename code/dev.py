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

subjectLiist = ['P54'] #Athlete_03, Athlete_03_MRI_BG 'Athlete_03_MRI_Katya' P54
session = 'walking' # 25_03_31  22_07_06
trial = 'Walking03'  # 'Walking_02', 'Squat_35kg_01', 'Squat_bw_01'

calibration_trials = ['Walking03']

class Run():
        def __init__(self):
                self.ik = True
                self.id = False
                self.ma = False
                self.so = False
                self.emg_normalise = False
                self.emg_scale = False
                self.emg_convert = True

                self.ceinms_model = False
                self.ceinms_input_data = True
                self.ceinms_calibration_cfg = False
                self.ceinms_calibration_setup = False
                self.ceinms_excitation_generator = False

                self.ceinms_calibration = False
                self.plot_ceinms_model_parameters = False
                self.plot_ceinms_calibration_results = False

                self.create_ceinms_exe_cfg = True
                self.create_ceinms_exe_setup = True

                self.ceinms_exe_loop = False

                self.ceinms_exe = True
                self.create_ceinms_optimise_setup = False
                self.ceinms_optimise = False

                self.jra_ceinms = True
                self.jra = True

                self.plot_muscle_forces = True

                self.push_trial_results_to_git = True


for subject in subjectLiist:
                
        trialPath = os.path.join(utils.SIMULATIONS_DIR, subject, session, trial)
        print(f'Analyzing trial at path: {trialPath}')
        analysis = utils.Analyse(trialPath)

        analysis.replace = True

        if not hasattr(analysis, 'path'):
                print("Analysis has no 'path' attribute, skipping this subject.")
                continue

        #%% Load settings
        if False:  analysis.reset_settings_xml()

        # print main inputs
        print("Main inputs:")
        print(f"Model file: {analysis.model_dir}")
        print(f"time range: {analysis.time_range}")
        print(f"IK file: {analysis.ik}")

        new_model = os.path.join(utils.MODELS_DIR, subject, session, 'scaled_opt_N10.osim')
        analysis.update_model(new_model)

        if Run().emg_convert:
                analysis.convert_mot_to_sto(attr='emg_normalised')
                analysis.update_trial_attribute(attr_name='emg_plot', new_value=analysis.emg_normalised)
                analysis.update_trial_attribute(attr_name='ceinms_excitations', new_value=analysis.emg_normalised)
        breakpoint()

        if Run().ik: analysis.run_ik()
        if Run().id: analysis.run_id()
        if Run().ma: analysis.run_ma()
        if Run().so: analysis.run_so()

        if Run().emg_normalise: analysis.run_emg_normalise()
        if Run().emg_scale:  analysis.scale_emg(scale_factor=0.70)

        #%% CEINMS setups
        if Run().ceinms_model:  analysis.create_ceinms_model()
        if Run().ceinms_input_data:  analysis.create_ceinms_input_data()

        if Run().ceinms_calibration_cfg:  analysis.create_ceinms_calibration_cfg(calibration_trial_names=calibration_trials)

        if Run().ceinms_calibration_setup:  analysis.create_ceinms_calibration_setup()

        if Run().ceinms_excitation_generator:  analysis.create_excitation_generator()

        #%% CEINMS calibration and optimization
        if Run().ceinms_calibration:  analysis.run_ceinms_calibration()
        if Run().plot_ceinms_model_parameters:  ceinms.plot_ceinms_model_parameters(os.path.join(analysis.path, '..\subjectCalibrated.xml'))
        if Run().plot_ceinms_calibration_results:  ceinms.plot_ceinms_calibration_results(setupXML_path=analysis.ceinms_calibration_setup)
        if Run().plot_ceinms_calibration_results:  ceinms.plot_compare_ceinms_models(analysis.ceinms_uncalibrated_model, analysis.ceinms_calibrated_model)

        if Run().create_ceinms_exe_cfg:  analysis.create_ceinms_exe_cfg()

        if Run().create_ceinms_exe_setup:  analysis.create_ceinms_exe_setup()

        if Run().ceinms_exe_loop:  analysis.run_ceinms_exe_loop()
        if Run().ceinms_exe:  analysis.run_ceinms_exe()
        if Run().create_ceinms_optimise_setup:  analysis.create_ceinms_optimise_setup()
        if Run().ceinms_optimise:  analysis.run_ceinms_optimise()

        if Run().jra_ceinms:      
                # analysis.replace = True
                # new_model = os.path.join(utils.MODELS_DIR, subject, session, 'scaled.osim')
                analysis.update_model(new_model)
                analysis.run_jra_ceinms()

        if Run().jra:      
                # analysis.replace = True
                # new_model = os.path.join(utils.MODELS_DIR, subject, session, 'scaled_increased_3.00.osim')
                analysis.update_model(new_model)
                analysis.run_jra()


        if Run().plot_muscle_forces:  ceinms.plot_ceinms_muscle_forces(analysis.jra_forces_ceinms)

        if Run().push_trial_results_to_git: analysis.push_trial_results_to_git()

        