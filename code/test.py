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

trialPath = os.path.join(utils.SIMULATIONS_DIR, 'Athlete_03', '25_03_31_calibration_constrained', 'Squat_35kg_01') # Walking_02, Squat_35kg_01
print(f'Analyzing trial at path: {trialPath}')

analysis = utils.Analyse(trialPath)

trialPath = r"C:\Git\Fatigue-prediction-MSC-Thesis\data\simulations\012\pre\Run_baselineA1"
print(f'Analyzing trial at path: {trialPath}')

analysis = utils.Analyse(trialPath)

# analysis.reset_settings_xml()
# print main inputs
print("Main inputs:")
print(f"Model file: {analysis.model_dir}")
print(f"time range: {analysis.time_range}")
print(f"IK file: {analysis.ik}")

def plot_summary(analysis):
        '''
        plot summary of all analyses for the trial
        
        row 1 - IK joint angles
        row 2 - ID joint moments and CEINMS joint moments
        row 3 - SO muscle forces and CEINMS forces
        row 4 - EMG excitations, SO activations, CEINMS activations
        row 5 - Norm Fiber lengths
        row 6 - Joint Reaction Forces
        '''
        # load all data
        analysis.joint_angles = load_any_data_file(analysis.ik)
        analysis.inverse_dynamics = load_any_data_file(analysis.id)
        analysis.so_forces = load_any_data_file(analysis.so_forces)
        analysis.so_activations = load_any_data_file(analysis.so_activations)
        analysis.jra_results = load_any_data_file(analysis.jra)
        analysis.emg_data = load_any_data_file(analysis.emg_normalised)

        setupXML = ET.parse(analysis.ceinms_exe_setup).getroot()
        ceinms_output_dir = os.path.join(analysis.path, setupXML.find('outputDirectory').text)

        analysis.ceinms_activations = load_any_data_file(os.path.join(ceinms_output_dir, 'Activations.sto'))
        analysis.ceinms_forces = load_any_data_file(os.path.join(ceinms_output_dir, 'MuscleForces.sto'))

        analysis.norm_fiber_lengths = load_any_data_file(os.path.join(ceinms_output_dir, 'NormFiberLengths.sto'))
        
        dofs = ['hip_flexion_r', 'knee_angle_r', 'ankle_angle_r']
        emg_mapping = analysis.EMG_muscle_mapping
        breakpoint()

        n_rows = 6
        fig, axes = plt.subplots(n_rows, 1, figsize=(15, n_rows*4), constrained_layout=True)



# plot_summary(analysis)

# analysis.run_ik()
# analysis.run_id()
# analysis.run_ma()
# analysis.run_so()
# analysis.run_jra()
# analysis.run_emg_normalise()
# analysis.scale_emg(scale_factor=0.70)
# analysis.create_ceinms_input_data()
# analysis.run_ceinms_calibration()
# analysis.create_ceinms_exe_setup()
# analysis.create_ceinms_exe_cfg()
# analysis.run_ceinms_exe_loop()
# analysis.run_ceinms_exe()
analysis.create_ceinms_optimise_setup()
analysis.run_ceinms_optimise()
# analysis.run_jra_ceinms()
# analysis.run_jra()

analysis.push_trial_results_to_git()

    


            

