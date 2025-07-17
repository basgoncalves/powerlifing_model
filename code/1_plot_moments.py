import os
import numpy as np
import utils
import paths
import opensim as osim
import matplotlib.pyplot as plt
import paths
from matplotlib.lines import Line2D

base_name = paths.SIMULATION_DIR
subjects = os.listdir(base_name)

file_to_plot = ['inverse_dynamics.sto']

columns = [
    # Only right side moments (for plotting both legs together, use _r and _l in loop)
    'hip_flexion_LEG_moment', 'hip_adduction_LEG_moment', 'hip_rotation_LEG_moment',
    'knee_angle_LEG_moment', 'knee_rotation_LEG_moment', 'knee_adduction_LEG_moment',
    'ankle_angle_LEG_moment',
    'subtalar_angle_LEG_moment',
    'mtp_angle_LEG_moment'
]
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
        try:
            trial = paths.Trial(subject_name=subject, session_name='22_07_06', trial_name=trial_name)
            data_trial = utils.load_any_data_file(trial.outputFiles['ID'].abspath())

            # split data left and right
            # breakpoint()  # This will pause the execution for debugging
            grouped_trials[subject].append(data_trial)
            
            print(f"Data for trial {trial.name}: {trial.outputFiles['ID'].abspath()}")
        except Exception as e:
            print(f"Error loading data for trial {trial.outputFiles['ID'].abspath()}: {e}")
            continue


# Create a figure for the plots
plt.figure(figsize=(12, 8))
n_subplots = len(columns)

# Calculate the number of rows and columns for subplots to make it without free cells in the bottom row
ncols = int(np.ceil(np.sqrt(n_subplots))).__round__()
nrows = int(np.ceil(n_subplots / ncols)).__round__()

fig, axs = plt.subplots(nrows, ncols, figsize=(15, 10), squeeze=False)
axs = axs.flatten()
lines = []

# Loop through each subject and their trials
for subject, trials in grouped_trials.items():
    for i, trial_data in enumerate(trials):
    
        trial_name = trial_list[i]
        
        time_norm_data = utils.time_normalise_df(trial_data)
        time_vector = np.linspace(0, 1, len(time_norm_data))
        
        
        for i, col in enumerate(columns):
            
            # breakpoint()  # This will pause the execution for debugging                
            # Plot data for each column, per trial, per subject, PER LEG 
            lines.append(axs[i].plot(time_vector, 
                                        time_norm_data[col.replace('_LEG_', '_r_')], 
                                        label=f"{trial_name} - 'right",
                                        color=plot_trials[trial_name]['color'], 
                                        linestyle=plot_model[subject]['linestyle'],
                                        alpha=plot_leg['r']['alpha']))

            lines.append(axs[i].plot(time_vector, 
                                        time_norm_data[col.replace('_LEG_', '_l_')], 
                                        label=f"{trial_name} - 'left",
                                        color=plot_trials[trial_name]['color'],
                                        linestyle=plot_model[subject]['linestyle'],
                                        alpha=plot_leg['l']['alpha']))
            
            # Set title and labels for each subplot
            axs[i].set_title(col)
            axs[i].set_xlabel('Time (s)')
            axs[i].set_ylabel('Moment (N*m)')

# Set legend only for the last subplot that has data
ax = axs[0]

handles, labels = ax.get_legend_handles_labels()
by_label = dict(zip(labels, handles))
# Build a custom legend based on plot_model, plot_trials, and plot_leg without repeats

legend_elements = []

# Add trial color legend
for trial, props in plot_trials.items():
    legend_elements.append(Line2D([0], [0], color=props['color'], lw=2, label=trial))

# Add subject linestyle legend
for subject, props in plot_model.items():
    legend_elements.append(Line2D([0], [0], color='black', linestyle=props['linestyle'], lw=2, label=subject))

# Add leg alpha legend
for leg, props in plot_leg.items():
    legend_elements.append(Line2D([0], [0], color='black', lw=2, alpha=props['alpha'], label=f"{'right' if leg == 'r' else 'left'} leg"))

ax.legend(handles=legend_elements, loc='upper right', fontsize='small', ncol=2)
ax.legend(by_label.values(), by_label.keys(), loc='upper right', fontsize='small', ncol=2)


# get screen size
screen_width, screen_height = utils.get_screen_size()
# Set the figure size to 90% of the screen size
fig.set_size_inches(screen_width * 0.9 / fig.dpi, screen_height * 0.9 / fig.dpi)
# Adjust the layout to prevent overlap
plt.tight_layout()
plt.subplots_adjust(hspace=0.3, wspace=0.2)

# save the figure
plt.savefig(os.path.join(paths.RESULTS_DIR, 'moments.png'), dpi=300, bbox_inches='tight')

print("Plots saved successfully.")
print(f'saved to: {os.path.join(paths.RESULTS_DIR, "moments.png")}')
