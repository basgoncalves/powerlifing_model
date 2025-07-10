# %%
import matplotlib.pyplot as plt
import pandas as pd
import os

from stan_utils import *

import time
from concurrent.futures import ProcessPoolExecutor

# ensure correct individual name
root = 'c:\\Users\\ebuly\\OneDrive\\Documents\\WORK\\JRF_GaitAnalysis'
cwd = os.getcwd()
tmp = cwd.split('\\')[len(root.split('\\')):]
ind = 'P' + tmp[0][1:]
ind
# %%
walking_dirs = os.listdir('walking')

# %%
def compare_models_one_trial(path_to_one, path_to_two, table_name, output_path):
    # dataframes
    if table_name[-3:] == 'csv':
        df_one = pd.read_csv(os.path.join(path_to_one,  table_name), index_col = 0)
        df_two = pd.read_csv(os.path.join(path_to_two,  table_name), index_col = 0)
    else:
        df_one = read_from_storage(os.path.join(path_to_one,  table_name))
        df_two = read_from_storage(os.path.join(path_to_two, table_name))

    model_one = path_to_one.split('/')[0]
    model_two = path_to_two.split('/')[0]
    
    # plot name
    name_parts = table_name.split('_')
    table = (' ').join(name_parts[2:])
    table = table_name.split('.')[0]

    # subplot names
    column_names = list(df_one.columns)
    for name in column_names:
        if 'Unnamed' in name:
            column_names.remove(name)

    # subplot number
    n = len(column_names)

    # columns and rows
    cols = 4
    if n % cols == 0: rows = n//cols
    else: rows = n//cols + 1

    # figure assembley
    fig, axs = plt.subplots(rows, cols, figsize = (cols*3,rows*3), constrained_layout=True)
    fig.suptitle(f'compare {table}', fontsize=18)
    count = 0
    while count < cols*rows:
        if count < n:
            for name in column_names:
                i = count // cols 
                j = count % cols
                axs[i,j].plot(df_one.index, df_one[name], label=name, color = 'g')                   
                axs[i,j].plot(df_two.index, df_two[name], label=name, color = 'orange')      
                
                axs[i,j].set_title(two_line_label (name))
                axs[i,j].set_axis_on()          
                
                count += 1
        else: 
            axs.flat[count].set_visible(False)
            count += 1

    # custom legend
        custom_lines = [plt.Line2D([0], [0], color='g', lw=2),
                        plt.Line2D([0], [0], color='orange', lw=2)]
        fig.legend(custom_lines, [model_one, model_two],  bbox_to_anchor=(0.5, 0., 0.5, 0.),
                    prop={'size': 13}, borderaxespad=0.1, ncol=6, labelspacing=0.)

    fig.get_layout_engine().set(h_pad=0.2)
    
    # save plot
    plt.savefig(os.path.join(output_path, f'{table}_compare_models.svg'), format = 'svg')
    

# %%
path_to_data_one = f'results_{ind}_tps_fibres_skin_wrp_updated/walking'
path_to_data_two = f'results_scaled_model_{ind}/walking'


# %%
def process_muscles(folder):
    ma_time_series_files = ['hip_rot_muscle_moment_arms.csv',
                        'hip_flex_muscle_moment_arms.csv',
                        'hip_add_muscle_moment_arms.csv',
                        'knee_flex_muscle_moment_arms.csv',
                        'ankle_flex_muscle_moment_arms.csv']
    for tab in ma_time_series_files:
        path_to_one = os.path.join(path_to_data_one, folder, 'muscle_moment_arms')
        path_to_two = os.path.join(path_to_data_two, folder, 'muscle_moment_arms')
        output_path = os.path.join('walking', folder)
        compare_models_one_trial(path_to_one, path_to_two, tab, output_path)
        plt.close()

# %%
def process_ik_id(folder):
    other_tables = ['IK_results.mot', 'ID_results.mot']
    for tab in other_tables:
        path_to_one = os.path.join(path_to_data_one, folder)
        path_to_two = os.path.join(path_to_data_two, folder)
        output_path = os.path.join('walking', folder)
        compare_models_one_trial(path_to_one, path_to_two, tab, output_path)
        plt.close()

# %%
def process_so_jr(folder):
    other_tables = ['SO_StaticOptimization_activation.sto','JR_JointReaction_ReactionLoads.sto']
    for tab in other_tables:
        path_to_one = os.path.join(path_to_data_one, folder, 'SO_Results')
        path_to_two = os.path.join(path_to_data_two, folder, 'SO_Results')
        output_path = os.path.join('walking', folder)
        compare_models_one_trial(path_to_one, path_to_two, tab, output_path)
        plt.close()

def process(folder):
    process_muscles(folder)
    process_ik_id(folder)
    process_so_jr(folder)

def main(walking_dirs):
    start_time = time.perf_counter()
    with ProcessPoolExecutor() as executor:
        executor.map(process, walking_dirs)
    duration = time.perf_counter() - start_time
    print(f"Computed in {duration} seconds")

if __name__ == "__main__":
    main(walking_dirs)