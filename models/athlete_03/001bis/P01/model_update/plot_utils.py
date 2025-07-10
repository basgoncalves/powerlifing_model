# Here I use a pd dataframe that would have been created by applying 'read_from_storage' from stan_utils.py
# The dataframe should have index and a column 'Time'
import pandas as pd
import numpy as np 
from  scipy import interpolate
from stan_utils import *
from matplotlib.lines import Line2D
import matplotlib.gridspec as gridspec
from interpDFrame import *
#import matplotlib as plt

import warnings
warnings.filterwarnings('ignore')

pd.options.mode.chained_assignment = None # to disable warnings


def extract_events(dataframe, min_value = 0, name_pattern = 'force_vy'):
    events = {}
    dataframe.index = range(dataframe.shape[0])
    for colname in dataframe.columns:
        if name_pattern in colname:
            for i in range(1, dataframe.shape[0]):
                if dataframe.at[i, colname] > min_value and  min_value >= dataframe.at[(i - 1), colname]:
                    events[dataframe.at[i, 'time']] = int(colname[5])

                elif dataframe.at[(i - 1), colname] > min_value and min_value >= dataframe.at[i, colname]:
                    events[dataframe.at[i, 'time']] = int(colname[5])
    return events

"""def save_standard_steps(dir, results_file='ID_results.mot', analysis_tag='ID_', grf_file='task_grf.mot', grf_pattern ='force_vy', odd_foot = '_r'):
    results=read_from_storage(os.path.join(dir, results_file), sampling_interval=0.01,to_filter=False)
    grf = read_from_storage(os.path.join(dir, grf_file), sampling_interval=0.01,to_filter=False)
    grf.index = range(grf.shape[0])
    events = extract_events(grf, min_value = 0,  name_pattern=grf_pattern)
    ev_t=list(events.values())
    n_of_steps = len(ev_t)//2

    if n_of_steps >= 4:
        # walking, 5 plates
        odd_stride1 = interpDFrame(results, ev_t[0], ev_t[3], 0)
        even_stride = interpDFrame(results, ev_t[1], ev_t[5], 0)
        odd_stride2 = interpDFrame(results, ev_t[3], ev_t[7], 0)
        df = pd.concat((odd_stride1, odd_stride2))
        by_row_index = df.groupby(df.index)
        odd_stride = by_row_index.mean()

    if n_of_steps <= 2:
        # running - steps do not overlap
        half_step_time = 0.5*(ev_t[3] - ev_t[0])
        odd_stride = interpDFrame(results, (ev_t[0] + (0.5 * (ev_t[1] - ev_t[0])) - half_step_time), (ev_t[0] + (0.5 * (ev_t[1] - ev_t[0])) + half_step_time), 0)
        even_stride = interpDFrame(results, (ev_t[2] + (0.5 * (ev_t[2] - ev_t[3])) - half_step_time), (ev_t[2] + (0.5 * (ev_t[2] - ev_t[3])) + half_step_time), 0)
        
    else:
        # walking, 3 plates
        odd_stride = interpDFrame(results, ev_t[0], ev_t[3], 0)
        even_stride = interpDFrame(results, ev_t[1], (ev_t[1] + (ev_t[3] - ev_t[0])), 0)

    odd_stride.to_csv(os.path.join(dir, f'{analysis_tag}standard_step{odd_foot}.csv'))
    if odd_foot == '_r':
        even_stride.to_csv(os.path.join(dir, f'{analysis_tag}standard_step_l.csv'))
    else: even_stride.to_csv(os.path.join(dir, f'{analysis_tag}standard_step_r.csv'))"""


"""def plot_standard_step(dir, results_file='ID_results.mot', grf_file='task_grf.mot', grf_pattern ='force_vy', odd_foot = '_r'):
    results=read_from_storage(os.path.join(dir, results_file), sampling_interval=0.01,to_filter=False)
    grf = read_from_storage(os.path.join(dir, grf_file), sampling_interval=0.01,to_filter=False)
    grf.index = range(grf.shape[0])
    events = extract_events(grf, min_value = 0,  name_pattern=grf_pattern)
    ev_t=list(events.values())
    n_of_steps = len(ev_t)//2
    half_step_time = 0.5*(ev_t[3] - ev_t[0])
    
    if n_of_steps > 3:
        # walking - steps overlap - 5 plates
        odd_stride = interpDFrame(results, ev_t[0], ev_t[3] , 0)
        even_stride = interpDFrame(results, ev_t[1], ev_t[5] , 0)
    
    if n_of_steps <= 2:
        # running - steps do not overlap
        odd_stride = interpDFrame(results, (ev_t[0] + (0.5 * (ev_t[1] - ev_t[0])) - half_step_time), (ev_t[0] + (0.5 * (ev_t[1] - ev_t[0])) + half_step_time), 0)
        even_stride = interpDFrame(results, (ev_t[2] + (0.5 * (ev_t[2] - ev_t[3])) - half_step_time), (ev_t[2] + (0.5 * (ev_t[2] - ev_t[3])) + half_step_time), 0)

    else:
        # walking - steps overlap - 3 plates
        odd_stride = interpDFrame(results, ev_t[0], ev_t[3] , 0)
        even_stride = interpDFrame(results, ev_t[1], (ev_t[1] + (ev_t[3] - ev_t[0])), 0)
        
        #odd_stride = interpDFrame(results, (ev_t[0] + (0.5 * (ev_t[2] - ev_t[0])) - half_step_time), (ev_t[0]+ (0.5 * (ev_t[2] - ev_t[0]))  + half_step_time), 0)
        #even_stride = interpDFrame(results, (ev_t[1] + (0.5 * (ev_t[4] - ev_t[1])) - half_step_time), (ev_t[1] + (0.5 * (ev_t[4] - ev_t[1])) + half_step_time), 0)

    rows_per_page = 4
    cols = 2
   
    cols_list = (odd_stride.columns)[1:]
    n = odd_stride.shape[1]-1
    nrows = 2*int(np.ceil(float(n) / cols))
    pages = int(np.ceil(float(nrows) / rows_per_page))"""

"""    with PdfPages(os.path.join(dir, results_file[:-4]+'_by_step.pdf')) as pdf:   
        for page in range(0, pages):
            fig, axs = plt.subplots(nrows=rows_per_page, ncols=cols, figsize=(8,12))
            #axs = axs.flatten()
            if odd_foot == '_r': color1 = 'g'; color2 = 'r'
            elif odd_foot == '_l': color1 = 'r'; color2 = 'g'
            for i, item in enumerate(cols_list[int((page*rows_per_page*cols*0.5)):int((page*rows_per_page*cols*0.5 + 0.5*rows_per_page*cols))]):
                axs[i, 0].plot(odd_stride['percentgaitcycle'], odd_stride[item], color = color1)
                axs[i, 0].set_title(two_line_label(item))
                if n_of_steps > 1: 
                    axs[i, 1].plot(odd_stride['percentgaitcycle'], even_stride[item], color = color2)
                    axs[i, 1].set_title(two_line_label(item))
            
            custom_lines = [Line2D([0], [0], color='g', lw=2), Line2D([0], [0], color='r', lw=2)]
            fig.legend(custom_lines, ['right', 'left'])
            fig.tight_layout()
            pdf.savefig(fig)
            plt.close()"""

# the tuple should contain more than one dataframe
def average_dataframe(tuple_of_dataframes):
    concat_df = pd.concat(tuple_of_dataframes)
    by_row_index = concat_df(concat_df.index)
    df_mean = by_row_index.mean()
    df_sd = by_row_index.sd()
    return df_mean, df_sd


# working_dir = path and name; list_of_folders = list of strings; list_first_foot = list of strings; results_file = string, file name; grf_file = string, file name
# produces mean and standard deviation dataframes for right and left legs
def assemble_average_steps_walking(working_dir, list_of_folders, list_first_foot, results_file, grf_file, grf_pattern ='force_vy', only_odd = False, filter_set = False):      
    df_concat_right = pd.DataFrame()
    df_concat_left = pd.DataFrame()

    for i, folder in enumerate(list_of_folders): 
        # input 
        input_dir = os.path.abspath(os.path.join(working_dir, folder))
        results_path = os.path.join(input_dir, results_file)
        grf_path = os.path.join(input_dir, grf_file)
        first_foot = list_first_foot[i]
        
        results=read_from_storage(results_path, sampling_interval=0.01,to_filter=filter_set)
        grf = read_from_storage(grf_path, sampling_interval=0.01,to_filter=filter_set)
        grf.index = range(grf.shape[0])

        events = extract_events(grf, min_value = 0,  name_pattern=grf_pattern)
        ev_t=list(events.keys())
        n_of_steps = len(ev_t)//2

        if n_of_steps == 5:
            # walking - steps overlap - 5 plates; the code includes time from heal strike to heal strike
            odd_stride1 = interpDFrame(results, ev_t[0], ev_t[4] , 0)
            odd_stride2 = interpDFrame(results, ev_t[4], ev_t[8] , 0)
            even_stride1 = interpDFrame(results, ev_t[2], ev_t[6] , 0)
            even_stride2 = interpDFrame(results, ev_t[6] , ev_t[9] - (ev_t[6] - ev_t[5]), 0)

            df_concat_odd = pd.concat((odd_stride1, odd_stride2))
            df_concat_even = pd.concat((even_stride1, even_stride2))

            if first_foot == '_r': df_toAdd_right = df_concat_odd.copy(); df_toAdd_left = df_concat_even.copy()                   
            else: df_toAdd_right = df_concat_even.copy(); df_toAdd_left = df_concat_odd.copy()

            if df_concat_right.shape == (0,0):
                df_concat_right = df_toAdd_right.copy(); df_concat_left = df_toAdd_left.copy()
            else: df_concat_right = pd.concat((df_concat_right, df_toAdd_right)); df_concat_left = pd.concat((df_concat_left, df_toAdd_left))
    

        if n_of_steps == 3:
            # walking - steps overlap - 3 plates
            odd_stride = interpDFrame(results, ev_t[0], ev_t[4] , 0)
            even_stride = interpDFrame(results, ev_t[2], (ev_t[2] + (ev_t[4] - ev_t[0])), 0)

            if first_foot == '_r': df_toAdd_right = odd_stride.copy(); df_toAdd_left = even_stride.copy()                   
            else: df_toAdd_right = even_stride.copy(); df_toAdd_left = odd_stride.copy()

            if df_concat_right.shape == (0,0):
                df_concat_right = df_toAdd_right.copy(); df_concat_left = df_toAdd_left.copy()
            else: df_concat_right = pd.concat((df_concat_right, df_toAdd_right)); df_concat_left = pd.concat((df_concat_left, df_toAdd_left))

    by_row_index_right = df_concat_right.groupby(df_concat_right.index); by_row_index_left = df_concat_left.groupby(df_concat_left.index)
    df_mean_right = by_row_index_right.mean(); df_std_right = by_row_index_right.std()
    df_mean_left = by_row_index_left.mean(); df_std_left = by_row_index_left.std()

    return df_mean_right, df_std_right, df_mean_left, df_std_left


def assemble_average_steps_running(working_dir, list_of_folders, list_first_foot, results_file, grf_file, grf_pattern ='force_vy', only_odd = False, filter_set = False):      
    df_concat_right = pd.DataFrame()
    df_concat_left = pd.DataFrame()

    for i, folder in enumerate(list_of_folders): 
        # input 
        input_dir = os.path.abspath(os.path.join(working_dir, folder))
        results_path = os.path.join(input_dir, results_file)
        grf_path = os.path.join(input_dir, grf_file)
        first_foot = list_first_foot[i]
        
        results=read_from_storage(results_path, sampling_interval=0.01,to_filter=filter_set)
        grf = read_from_storage(grf_path, sampling_interval=0.01,to_filter=filter_set)
        grf.index = range(grf.shape[0])

        events = extract_events(grf, min_value = 0,  name_pattern=grf_pattern)
        ev_t=list(events.values())
        ev_t=list(events.keys())
        n_of_steps = len(ev_t)//2

        if n_of_steps <= 2:
            # running - steps do not overlap; only odd step is returned per trial
            half_stride = ev_t[2] - ev_t[0]
            odd_stride = interpDFrame(results, ev_t[0], ev_t[2] + half_stride, 0)

        if n_of_steps == 3:
            # steps could overlap - 3 plates
            odd_stride = interpDFrame(results, ev_t[0], ev_t[4], 0)

        if first_foot == '_r':
            if df_concat_right.shape == (0,0): df_concat_right = odd_stride.copy()
            else: df_concat_right = pd.concat((df_concat_right, odd_stride))
        if first_foot == '_l': 
            if df_concat_left.shape == (0,0): df_concat_left = odd_stride.copy()
            else: df_concat_left = pd.concat((df_concat_left, odd_stride))

    by_row_index_right = df_concat_right.groupby(df_concat_right.index); by_row_index_left = df_concat_left.groupby(df_concat_left.index)
    df_mean_right = by_row_index_right.mean(); df_std_right = by_row_index_right.std()
    df_mean_left = by_row_index_left.mean(); df_std_left = by_row_index_left.std()

    return df_mean_right, df_std_right, df_mean_left, df_std_left

def two_line_label (x):
    tag = x.split('_')
    n = len(tag)
    if n<=3:
        label = tag
    else:
        i = 0
        first_half = ''
        while i < n//2-1:
            first_half= first_half + tag[i] + ' '
            i+=1
        first_half = first_half + tag[i]
        second_half = ''
        while i < n-1:
            i+=1
            second_half = second_half + tag[i] + ' '
            label = first_half + '\n' + second_half
    return label

def plot_a_step(df_mean, df_std, list_of_columns, title = None, plots_per_row = 3, main_color='b', secondary_color = 'grey'):
    x = df_mean['percentgaitcycle']
    nrows = -(len(list_of_columns)//- plots_per_row)
    figsize = (3*plots_per_row, 3*nrows)
    fig, axs = plt.subplots(nrows, ncols=plots_per_row, figsize=figsize, constrained_layout=True)
    axs = axs.flatten()
    for i, item in enumerate(list_of_columns):
        axs[i].plot(x, df_mean[item], color = main_color)
        axs[i].fill_between(x, df_mean[item] + df_std[item], df_mean[item] - df_std[item], color = secondary_color, alpha = 0.2)
        axs[i].set_title(two_line_label(item))
    if title != None: fig.suptitle(title, fontsize = 14) #; , y=.995   fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    #fig.tight_layout()
    #plt.subplots_adjust(top=0.9)
    fig.subplots_adjust(wspace=0.05)
    plt.show


def plot_data(df, list_of_columns = None, title = None, plots_per_row = 3, main_color='b'):
    x = df.index
    if list_of_columns == None:
        list_of_columns = df.columns
    nrows = -(len(list_of_columns)//- plots_per_row)
    figsize = (3*plots_per_row, 3*nrows)
    fig, axs = plt.subplots(nrows, ncols=plots_per_row, figsize=figsize)
    axs = axs.flatten()
    for i, item in enumerate(list_of_columns):
        axs[i].plot(x, df[item], color = main_color)
        axs[i].set_title(two_line_label(item))
    if title != None: fig.suptitle(title, fontsize = 14, y=.995) #; fig.tight_layout(rect=[0, 0.03, 1, 0.95])
    fig.tight_layout()
    plt.show