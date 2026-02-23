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
import pandas as pd

subjectLiist = ['P54'] #Athlete_03, Athlete_03_MRI_BG 'Athlete_03_MRI_Katya' P54
session = 'walking' # 25_03_31  22_07_06
trial = 'Walking03'  # 'Walking_02', 'Squat_35kg_01', 'Squat_bw_01'

calibration_trials = ['Walking03']

class Batch():
        def __init__(self):
                self.ik = False
                self.id = False
                self.ma = False
                self.so = False
                self.emg_normalise = False
                self.emg_scale = False
                self.emg_convert = True

                self.ceinms_model = False
                self.ceinms_input_data = False
                self.ceinms_calibration_cfg = False
                self.ceinms_calibration_setup = False
                self.ceinms_excitation_generator = False

                self.ceinms_calibration = False
                self.plot_ceinms_model_parameters = False
                self.plot_ceinms_calibration_results = False

                self.create_ceinms_exe_cfg = False
                self.create_ceinms_exe_setup = True

                self.ceinms_exe_loop = False

                self.ceinms_exe = True
                self.create_ceinms_optimise_setup = False
                self.ceinms_optimise = False

                self.jra_ceinms = True
                self.jra = True

                self.plot_muscle_forces = True

                self.push_trial_results_to_git = True

        def print_attributes(self):
                attrs = vars(self)
                print("Batch class attributes and their values:")
                for attr, value in attrs.items():
                        print(f"{attr}: {value}")

        def inverse_kinematics(self):
                for subject in subjectLiist:
                        trialPath = os.path.join(utils.SIMULATIONS_DIR, subject, session, trial)
                        print(f'Analyzing trial at path: {trialPath}')
                        self.analysis = utils.Analyse(trialPath)

                        self.analysis.replace = False

                        if not hasattr(self.analysis, 'path'):
                                print("Analysis has no 'path' attribute, skipping this subject.")
                                continue

                        # print main inputs
                        print("Main inputs:")
                        print(f"Model file: {self.analysis.model_dir}")
                        print(f"time range: {self.analysis.time_range}")
                        print(f"IK file: {self.analysis.ik}")

                        new_model = os.path.join(utils.MODELS_DIR, subject, session, 'scaled_opt_N10.osim')
                        self.analysis.update_model(new_model)

                        self.analysis.run_ik()

        def subject_loop(self):

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

                        if self.emg_convert:
                                analysis.convert_mot_to_sto(attr='emg_normalised')
                                analysis.update_trial_attribute(attr_name='emg_plot', new_value=analysis.emg_normalised)
                                analysis.update_trial_attribute(attr_name='ceinms_excitations', new_value=analysis.emg_normalised)
                        breakpoint()

                        if self.ik: analysis.run_ik()
                        if self.id: analysis.run_id()
                        if self.ma: analysis.run_ma()
                        if self.so: analysis.run_so()

                        if self.emg_normalise: analysis.run_emg_normalise()
                        if self.emg_scale:  analysis.scale_emg(scale_factor=0.70)

                        #%% CEINMS setups
                        if self.ceinms_model:  analysis.create_ceinms_model()
                        if self.ceinms_input_data:  analysis.create_ceinms_input_data()
                        if self.ceinms_calibration_cfg:  analysis.create_ceinms_calibration_cfg(calibration_trial_names=calibration_trials)

                        if self.ceinms_calibration_setup:  analysis.create_ceinms_calibration_setup()

                        if self.ceinms_excitation_generator:  analysis.create_excitation_generator()

                        #%% CEINMS calibration and optimization
                        if self.ceinms_calibration:  analysis.run_ceinms_calibration()
                        if self.plot_ceinms_model_parameters:  ceinms.plot_ceinms_model_parameters(os.path.join(analysis.path, '..\subjectCalibrated.xml'))
                        if self.plot_ceinms_calibration_results:  ceinms.plot_ceinms_calibration_results(setupXML_path=analysis.ceinms_calibration_setup)
                        if self.plot_ceinms_calibration_results:  ceinms.plot_compare_ceinms_models(analysis.ceinms_uncalibrated_model, analysis.ceinms_calibrated_model)

                        if self.create_ceinms_exe_cfg:  analysis.create_ceinms_exe_cfg()

                        if self.create_ceinms_exe_setup:  analysis.create_ceinms_exe_setup()

                        if self.ceinms_exe_loop:  analysis.run_ceinms_exe_loop()
                        if self.ceinms_exe:  analysis.run_ceinms_exe()
                        if self.create_ceinms_optimise_setup:  analysis.create_ceinms_optimise_setup()
                        if self.ceinms_optimise:  analysis.run_ceinms_optimise()

                        if self.jra_ceinms:      
                                # analysis.replace = True
                                # new_model = os.path.join(utils.MODELS_DIR, subject, session, 'scaled.osim')
                                analysis.update_model(new_model)
                                analysis.run_jra_ceinms()

                        if self.jra:      
                                # analysis.replace = True
                                # new_model = os.path.join(utils.MODELS_DIR, subject, session, 'scaled_increased_3.00.osim')
                                analysis.update_model(new_model)
                                analysis.run_jra()


                        if self.plot_muscle_forces:  ceinms.plot_ceinms_muscle_forces(analysis.jra_forces_ceinms)

                        if self.push_trial_results_to_git: analysis.push_trial_results_to_git()

from sklearn.metrics import mean_squared_error, r2_score

def plot_muscle_forces_3_tasks(tasks, muscleGroups, tasks_figures, results_dir, colors, font_size, forces_type='so'):
    '''Function to plot muscle forces for multiple tasks and muscle groups.

    Parameters:
    tasks (dict): Dictionary with task names as keys and tuples of (scaled_trials, mri_trials) as values.
    muscleGroups (dict): Dictionary with muscle group names as keys and lists of muscle names as values.
    tasks_figures (dict): Dictionary with task names as keys and paths to task figure images as values.
    results_dir (str): Directory to save the resulting plot.
    colors (dict): Dictionary with color codes for 'scaled' and 'MRI_BG'.
    font_size (int): Font size for plot titles and labels.
    forces_type (str): Type of muscle forces to plot ('so' for Static Optimization, 'ceinms' for CEINMS).

    '''    
        
    fig, axes = plt.subplots(nrows=len(tasks), ncols=len(muscleGroups)+1, figsize=(150, 25),
                        gridspec_kw={'width_ratios': [1] + [2]*len(muscleGroups), 'wspace': 0.3})

    for task_idx, (task_name, (scaled_trials, mri_trials)) in enumerate(tasks.items()):
        
        # Add task figure in the first column
        task_fig_path = tasks_figures[task_name]
        utils.add_picture_to_ax(axes[task_idx, 0], task_fig_path, scale=1.0)

        # Load results for all trials
        if forces_type == 'so':
            scaled_dfs = [utils.load_any_data_file(os.path.join(trial.path, trial.so_forces)) for trial in scaled_trials]
            mri_dfs = [utils.load_any_data_file(os.path.join(trial.path, trial.so_forces)) for trial in mri_trials]
        elif forces_type == 'ceinms':
            scaled_dfs = [utils.load_any_data_file(os.path.join(trial.path, trial.jra_forces_ceinms)) for trial in scaled_trials]
            mri_dfs = [utils.load_any_data_file(os.path.join(trial.path, trial.jra_forces_ceinms)) for trial in mri_trials]
                    
        # Plot each muscle group
        for muscle_idx, (group_name, muscles) in enumerate(muscleGroups.items()):
            col_idx = muscle_idx + 1
            ax = axes[task_idx, col_idx]

            scaled_dfs = [df.copy() for df in scaled_dfs]
            for df in scaled_dfs:
                df[group_name] = df[muscles].sum(axis=1)

            mri_dfs = [df.copy() for df in mri_dfs]
            for df in mri_dfs:
                df[group_name] = df[muscles].sum(axis=1)

            ax = utils.plot_mean_error_shade(ax, scaled_dfs, 'time', group_name, colors['Cateli'], label='Cateli')
                    
            ax = utils.plot_mean_error_shade(ax, mri_dfs, 'time', group_name, colors['Lernagopal'], label='Lernagopal')

            ax.set_label(f'{group_name}')
            ax.set_title(f'{group_name}', fontsize=font_size)
            ax.tick_params(axis='both', which='major', labelsize=font_size)
            ax.grid(True)

            # add RMSE and R2 between scaled and mri
            scaled_mean = pd.concat(scaled_dfs)[group_name].values # Get mean values for scaled and MRI
            mri_mean = pd.concat(mri_dfs)[group_name].values

            min_len = min(len(scaled_mean), len(mri_mean)) # Ensure same length by interpolation or trimming
            scaled_mean = scaled_mean[:min_len]
            mri_mean = mri_mean[:min_len]

            rmse = utils.rmse(scaled_mean, mri_mean)
            r2 = utils.rsquared(scaled_mean, mri_mean)

            # Add text box with metrics
            textstr = f'RMSE: {rmse:.2f} N\nR²: {r2:.3f}'
            props = dict(boxstyle='round', facecolor='wheat', alpha=0.5)
            ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=font_size-4,
                verticalalignment='top', bbox=props)
            
            if col_idx == 1:
                ax.set_ylabel('Force (N)', fontsize=font_size)

            # Add legend only to first data subplot
            if task_idx == 0 and col_idx == 1:
                ax.legend(fontsize=font_size)

    utils.mmfn(fig, n_rows=len(tasks), n_cols=len(muscleGroups)+1)
    save_path = os.path.join(results_dir, f'muscle_forces_{forces_type}.png')
    plt.savefig(save_path, dpi=150, bbox_inches='tight')
    print(f"{forces_type.upper()} comparison plot saved: {save_path}")

if __name__ == "__main__":
    
#     Batch().subject_loop()
#     Batch().inverse_kinematics()
        subject  = 'Athlete_03_Lernagopal_optimised'
        session = '25_03_31'
        trial = 'Squat_35kg_01' #'Squat_BW_01' Squat_35kg_01 Walking_02
        analyse = utils.Analyse(trialPath=os.path.join(utils.SIMULATIONS_DIR, subject, session, trial))

        # open the settings XML in the editor to check the new model path
        os.startfile(analyse.settingsXML)

        analyse.replace = True
        # analyse.run_so()
        # analyse.edit_model_range_coordinates(coordinate_name='knee_angle_r', new_range=[-2.44346, 0.17453293])

        # analyse.edit_model_range_coordinates(coordinate_name='knee_angle_l', new_range=[-2.44346, 0.17453293])

        # analyse.run_ik()
        # analyse.run_id()
        # analyse.run_ma()
        analyse.run_so()

        

# END       