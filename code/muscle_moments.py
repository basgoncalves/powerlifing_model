import utils
import os
import pandas as pd
import numpy as np
import xml.etree.ElementTree as ET
import opensim as osim
import os
import openSim
import ceinms
import c3d
import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
from scipy.signal import butter, filtfilt
import math

def plot_muscle_moments(ax: plt.Axes, trial: utils.Analyse, dof: str, forces: str = 'so'):
    '''
    Plots muscle moments for a given degree of freedom (DOF) on the provided axes.
    Parameters:
        - ax: The matplotlib axes to plot on.
        - trial: The trial data containing paths to the necessary files.
        - dof: The degree of freedom for which to plot the muscle moments (e.g., 'hip_flexion_r').
        - forces: The type of muscle forces to use ('so' for static optimization or 'ceinms' for electromyography informed optimization).
    '''
    moments = utils.load_any_data_file(os.path.join(trial.path, trial.id))

    if forces.lower() == 'so':
        muscle_forces = utils.load_any_data_file(os.path.join(trial.path, trial.so_forces))
    elif forces.lower() == 'ceinms':
        muscle_forces = utils.load_any_data_file(os.path.join(trial.path, trial.jra_forces_ceinms))
    ma_path = os.path.join(trial.path, trial.ma, f'_MuscleAnalysis_MomentArm_{dof}.sto')
    if not os.path.exists(ma_path):
        print(f"Moment arm file for {dof} not found in {trial.path}. Skipping muscle moment plot for this DOF.")
        return
    
    try:
        moment_arms = utils.load_any_data_file(os.path.join(trial.path, trial.ma, f'_MuscleAnalysis_MomentArm_{dof}.sto'))
    except:
        print(f"Moment arm file for {dof} not found in {trial.path}. Skipping muscle moment plot for this DOF.")
        return

    muscle_list = muscle_forces.columns.drop('time')

    muscles = openSim.find_non_zero_mom_arm_muscles(moment_arms, muscle_list)
    # print(f"Non-zero moment arm muscles for {dof}: {muscles}")

    muscle_moments = muscle_forces.multiply(moment_arms, axis=0)
    muscle_moments['time'] = muscle_forces['time']


    for muscle in muscles:
        ax.plot(muscle_moments['time'], muscle_moments[muscle], label=muscle, linestyle='--')

    ax.plot(moments['time'], moments[dof+'_moment'], label=f'Inverse Dynamics {model_name}', color=colors[model_name], linewidth=2)

    # Fill area without edge styling
    ax.fill_between(
        muscle_moments['time'],
        muscle_moments[muscles].sum(axis=1),
        alpha=0.3,
        color='gray',
    )

    # Add dashed outline separately
    ax.plot(
        muscle_moments['time'],
        muscle_moments[muscles].sum(axis=1),
        color='black',
        linestyle='--',
        linewidth=2,
        label='Total Muscle Moment'
    )

    # calculate the difference between the total muscle moment and the inverse dynamics moment and add it as text to the plot
    total_muscle_moment = muscle_moments[muscles].sum(axis=1)
    inverse_dynamics_moment = moments[dof+'_moment']
    moment_diff = total_muscle_moment - inverse_dynamics_moment
    moment_diff_mean = moment_diff.mean()
    moment_diff_std = moment_diff.std()

    moment_diff_mean_pct = (moment_diff_mean / (total_muscle_moment.max() - total_muscle_moment.min())) * 100
    moment_diff_std_pct = (moment_diff_std / (total_muscle_moment.max() - total_muscle_moment.min())) * 100

    text_str = f'Mean Residual: {moment_diff_mean:.2f} Nm ({moment_diff_mean_pct:.2f}%) \nStd: {moment_diff_std:.2f} Nm ({moment_diff_std_pct:.2f}%)'
    ax.text(0.02, 0.98, text_str, transform=ax.transAxes, fontsize=10, verticalalignment='top', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))


    save_path = save_path.replace('.png', '.html')
    utils.convert_to_interactive_fig(fig, save_path, launch_browser=False)
    print(f"Muscle moments comparison interactive plot saved: {save_path}")



if __name__ == "__main__":
    


    ik_columns = ['hip_flexion_r', 'hip_adduction_r', 'hip_rotation_r', 'knee_angle_r','knee_adduction_r', 'ankle_angle_r']
    id_columns = ['hip_flexion_r_moment', 'hip_adduction_r_moment', 'hip_rotation_r_moment', 'knee_angle_r_moment', 'knee_adduction_r_moment','ankle_angle_r_moment']

    muscleGroups = {
        'R Gluteus maximus': ['glmax1_r', 'glmax2_r', 'glmax3_r'],
        'R Gluteus medius': ['glmed1_r', 'glmed2_r', 'glmed3_r'],
        'R Gluteus minimus': ['glmin1_r', 'glmin2_r', 'glmin3_r'],
        'R Adductor Magnus': ['addmagDist_r', 'addmagIsch_r', 'addmagMid_r', 'addmagProx_r'],
        'R Biceps Femoris': ['bflh_r', 'bfsh_r'],
        'R Semimembranosus': ['semimem_r'],
        'R Semitendinosus': ['semiten_r'],
        'R Rectus Femoris': ['recfem_r'],
        'R Vasti': ['vasint_r', 'vaslat_r', 'vasmed_r'],
        'R Triceps Surae': ['soleus_r', 'gaslat_r', 'gasmed_r'],
        'L Gluteus maximus': ['glmax1_l', 'glmax2_l', 'glmax3_l'],
        'L Gluteus medius': ['glmed1_l', 'glmed2_l', 'glmed3_l'],
        'L Gluteus minimus': ['glmin1_l', 'glmin2_l', 'glmin3_l'],
        'L Adductor Magnus': ['addmagDist_l', 'addmagIsch_l', 'addmagMid_l', 'addmagProx_l'],
        'L Biceps Femoris': ['bflh_l', 'bfsh_l'],
        'L Semimembranosus': ['semimem_l'],
        'L Semitendinosus': ['semiten_l'],
        'L Rectus Femoris': ['recfem_l'],
        'L Vasti': ['vasint_l', 'vaslat_l', 'vasmed_l'],
        'L Triceps Surae': ['soleus_l', 'gaslat_l', 'gasmed_l'],
    }

    colors = {
        'HC835B_CUT_0001': 'green',
        'HC835B_OGR_0001': 'blue',
        'HC835B_OGW_0001': 'red'
    }

    forces_type = {
        'HC835B_CUT_0001': 'so',
        'HC835B_OGR_0001': 'so',
        'HC835B_OGW_0001': 'so'
    }

    lineStyles = {
        'HC835B_CUT_0001': '-',
        'HC835B_OGR_0001': '-',
        'HC835B_OGW_0001': '-'
    }

    variable_labels = {'Joint_Angles': ik_columns, 'Joint_Moments': id_columns, 'Muscle_Groups': muscleGroups}



    target_sessions = 'Session1'
    trial_prefixes = ['HC835B_OGR_0001', 'HC835B_OGW_0001', 'HC835B_CUT_0001']
    variables_of_interest = ['ik', 'id', 'so_forces']

    simulations_dir = utils.SIMULATIONS_DIR
    results_dir = utils.RESULTS_DIR + '_haie'

    results_file = os.path.join(results_dir, 'summary_data.csv')
    summary_df = pd.read_csv(results_file)


    subject = 'HC835B'

    labels = colors.keys()

    trials = {}
    for label, trialName in zip(labels, lineStyles.keys()):
        trialPath = os.path.join(utils.SIMULATIONS_DIR, subject, target_sessions, trialName)
        trials[label] = utils.Analyse(trialPath)


    fig, axes = plt.subplots(nrows=len(ik_columns), ncols=len(trials), figsize=(25, 15))

    for irow, dof in enumerate(ik_columns):
        for icol, model_name in enumerate(trials.keys()):
            ax = axes[irow, icol]
            plot_muscle_moments(ax, trials[model_name], dof, forces=forces_type[model_name])

            if icol == 0:
                ax.set_ylabel(f'{dof} (Nm)')
            
            if irow == len(ik_columns) - 1:
                ax.set_xlabel('Time (s)')
            elif irow == 0:
                ax.set_title(f'{model_name}', fontsize=12)

            if icol == len(trials) - 1 and irow == 0:
                ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small')

    # add sup title
    fig.suptitle(f'Muscle Moments Comparison - {subject}', fontsize=16, y=0.90)

    # Sync y-axis limits per row
    n_rows = len(ik_columns)
    n_cols = len(trials)
    for row_idx in range(n_rows):
        y_min = min(axes[row_idx, col_idx].get_ylim()[0] for col_idx in range(n_cols))
        y_max = max(axes[row_idx, col_idx].get_ylim()[1] for col_idx in range(n_cols))
        for col_idx in range(n_cols):
            axes[row_idx, col_idx].set_ylim(y_min, y_max)

    # save figure
    save_path = os.path.join(results_dir, f'muscle_moments_{subject}.png')
    fig.tight_layout(h_pad=2.0, w_pad=.5)
    fig.subplots_adjust(hspace=0.5, wspace=0.3) 
    fig.savefig(save_path, dpi=300)
    print(f"Muscle moments comparison plot saved: {save_path}")