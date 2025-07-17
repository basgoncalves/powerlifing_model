import os
from turtle import pd
import numpy as np
import utils
import paths
import opensim as osim
import matplotlib.pyplot as plt
import paths

base_name = paths.SIMULATION_DIR
subjects = os.listdir(base_name)

file_to_plot = 'SO_StaticOptimization_force'

columns = paths.Settings().plot['Groups'][file_to_plot]

# pelvis_rotation	pelvis_tilt	pelvis_list	pelvis_tx	pelvis_ty	pelvis_tz	hip_flexion_r	hip_adduction_r	hip_rotation_r	knee_angle_r	knee_rotation_r	knee_adduction_r	knee_angle_r_beta	ankle_angle_r	subtalar_angle_r	mtp_angle_r	hip_flexion_l	hip_adduction_l	hip_rotation_l	knee_angle_l	knee_rotation_l	knee_adduction_l	knee_angle_l_beta	ankle_angle_l	subtalar_angle_l	mtp_angle_l
columns_right = [col.replace('LEG', 'r') for col in columns]
columns_left = [col.replace('LEG', 'l') for col in columns]


trial_list = paths.Settings().TRIAL_TO_ANALYSE
analysis = {'Athlete_03_MRI': trial_list,
            'Athlete_03': trial_list}

grouped_trials = {'Athlete_03_MRI': [],
                  'Athlete_03': []}

# Define plotting styles for each subject
plot_model = {
    'Athlete_03_MRI': {'linestyle': '--'},
    'Athlete_03': {'linestyle': '-'}
}

plot_trials = {
    'sq_70': {'color': (0.0, 0.0, 1.0)},  # Blue
    'sq_75': {'color': (0.0, 1.0, 0.0)},  # Green
    'sq_80': {'color': (1.0, 0.0, 0.0)},  # Red
    'sq_85': {'color': (1.0, 0.5, 0.0)},  # Orange
    'sq_90': {'color': (0.5, 0.0, 0.5)},  # Purple
    'sq_95': {'color': (0.0, 1.0, 1.0)},  # Cyan
}
plot_leg = {
    'r': {'alpha': 0.4},
    'l': {'alpha': 1},
}

for trial_name in trial_list:  # Get all sessions for the subject
    for subject, _ in analysis.items():
        grouped_trials[subject] ={}
            
        try:
            # breakpoint()  # This will pause the execution for debugging
            trial = paths.Trial(subject_name=subject, session_name='22_07_06', trial_name=trial_name)
            data_trial = utils.load_any_data_file(trial.outputFiles['FORCES_SO'].abspath()) 
            # breakpoint()  # This will pause the execution for debugging
            for muscle, osim_list in columns.items():
                
                left_osim_list = [col.replace('_r', '_l') for col in osim_list]
                # breakpoint()  # This will pause the execution for debugging
                if muscle not in grouped_trials[subject]:
                    grouped_trials[subject][muscle] = {}
                if trial_name not in grouped_trials[subject][muscle]:
                    grouped_trials[subject][muscle][trial_name] = {}
                    
                grouped_trials[subject][muscle][trial_name] = {
                    'right': data_trial[osim_list].sum(axis=1),
                    'left': data_trial[left_osim_list].sum(axis=1)
                }

            print(f"Data for trial {trial.name}: {trial.outputFiles['FORCES_SO'].abspath()}")
        except Exception as e:
            print(f"Error loading data for trial {trial.outputFiles['FORCES_SO'].abspath()}: {e}")
            continue

# Create a figure for the plots
n_muscles = len(columns)
ncols = int(np.ceil(np.sqrt(n_muscles)))
nrows = int(np.ceil(n_muscles / ncols))

fig, axs = plt.subplots(nrows, ncols, figsize=(15, 10), squeeze=False)
axs = axs.flatten()

# Loop through each muscle (subplot)
for idx, (muscle, osim_list) in enumerate(columns.items()):
    ax = axs[idx]
    for subject, trials in grouped_trials.items():
        for trial_name in trial_list:
            if muscle not in trials or trial_name not in trials[muscle]:
                continue
            trial_data = trials[muscle][trial_name]
            for leg, leg_label in zip(['right', 'left'], ['r', 'l']):
                data = utils.pd.DataFrame(trial_data[leg])
                if data is None or len(data) == 0:
                    continue
                # Time normalization
                # breakpoint()  # This will pause the execution for debugging
                time_norm_data = utils.time_normalise_df(data, fs=100)  # Assuming 100 Hz sampling rate
                time_vector = np.linspace(0, 1, len(time_norm_data))
                ax.plot(
                    time_vector,
                    time_norm_data,
                    label=f"{subject} {trial_name} {leg_label}",
                    color=plot_trials[trial_name]['color'],
                    linestyle=plot_model[subject]['linestyle'],
                    alpha=plot_leg[leg_label]['alpha']
                )
    ax.set_title(muscle)
    ax.set_xlabel('Time (normalized)')
    ax.set_ylabel('Force (N)')
    ax.legend(fontsize='x-small')

# Hide unused subplots
for j in range(idx + 1, len(axs)):
    fig.delaxes(axs[j])

# get screen size
screen_width, screen_height = utils.get_screen_size()
fig.set_size_inches(screen_width * 0.9 / fig.dpi, screen_height * 0.9 / fig.dpi)
plt.tight_layout()
plt.subplots_adjust(hspace=0.3, wspace=0.2)

# save the figure
plt.savefig(os.path.join(paths.RESULTS_DIR, 'muscle_forces.png'), dpi=300, bbox_inches='tight')

print("Plots saved successfully.")
print(f'saved to: {os.path.join(paths.RESULTS_DIR, "muscle_forces.png")}')
