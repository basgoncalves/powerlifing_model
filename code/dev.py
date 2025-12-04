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

subject = 'Athlete_03'
session = '25_03_31'
trial = 'Walking_02'  # 'Walking_02', 'Squat_35kg_01', 'Squat_bw_01'


trialPath = os.path.join(utils.SIMULATIONS_DIR, subject, session, trial)
print(f'Analyzing trial at path: {trialPath}')
analysis = utils.Analyse(trialPath)

if False:  analysis.reset_settings_xml()

# print main inputs
print("Main inputs:")
print(f"Model file: {analysis.model_dir}")
print(f"time range: {analysis.time_range}")
print(f"IK file: {analysis.ik}")

if False: analysis.run_ik()
if False: analysis.run_id()
if False:  analysis.run_ma()
if False:  analysis.run_so()
if False:  analysis.run_jra()
if False:  analysis.run_emg_normalise()
if False:  analysis.scale_emg(scale_factor=0.70)

if False:  analysis.replace = False

if False:  analysis.create_ceinms_model()

if False:  analysis.create_ceinms_input_data()

if False:  analysis.create_ceinms_calibration_cfg(calibration_trial_names=['Squat_bw_01'])

if False:  analysis.create_ceinms_calibration_setup()

if False:  analysis.create_excitation_generator()

if False:  analysis.create_ceinms_exe_cfg()

if False:  analysis.create_ceinms_exe_setup()


if False:  analysis.run_ceinms_calibration()
if False:  ceinms.plot_ceinms_model_parameters(os.path.join(analysis.path, '..\subjectCalibrated.xml'))
if False:  ceinms.plot_ceinms_calibration_results(setupXML_path=analysis.ceinms_calibration_setup)

                                
if False:  analysis.create_ceinms_exe_setup()
if False:  analysis.create_ceinms_exe_cfg()
if False:  analysis.run_ceinms_exe_loop()
if False:  analysis.run_ceinms_exe()
if False:  analysis.create_ceinms_optimise_setup()
if False:  analysis.run_ceinms_optimise()


if True:      
        analysis.replace = True
        new_model = os.path.join(utils.MODELS_DIR, subject, session, 'scaled.osim')
        analysis.update_model(new_model)
        analysis.run_jra_ceinms()

if False:
        analysis.replace = True
        new_model = os.path.join(utils.MODELS_DIR, subject, session, 'scaled_increased_3.00.osim')
        analysis.update_model(new_model)
        analysis.run_jra()

if False: analysis.push_trial_results_to_git()

    

