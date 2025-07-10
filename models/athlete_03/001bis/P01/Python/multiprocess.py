import time
from concurrent.futures import ProcessPoolExecutor
from one_trial_pipeline import *

# import logging
# from datetime import datetime
# # note date and time
# date_time = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")
# # activate logger
# logger = logging.getLogger(__name__)
# logging.basicConfig(filename=f'{date_time}.log', format='%(asctime)s %(message)s', encoding='utf-8', level=logging.DEBUG)
# logging.getLogger('matplotlib.font_manager').disabled = True

walking_dirs = os.listdir('walking')
#walking_dirs.remove('Walking09')

root = 'c:\\Users\\User\\OneDrive\\Documents\\WORK\\JRF_GaitAnalysis'
cwd = os.getcwd()
tmp = cwd.split('\\')[len(root.split('\\')):]
ind = 'P' + tmp[0][1:]

individual_tag = ind

model_name =  f'{individual_tag}_tps_fibres_skin_wrp_updated.osim'
model_folder = os.path.join('../', 'model_update', '4_tps-bones-muscles-updated') 

# model_name =  f'scaled_model_{individual_tag}.osim'
# model_folder = os.path.join('../', 'model_update', '3a_osim_markers') 

tempalte_dir = os.path.abspath(os.path.join('../', 'templates'))
actuator_file = os.path.join(tempalte_dir, 'final_actuators.xml')
first_foot_file_name = 'steps.txt'

# create results dir
results_dir = f'results_{model_name[:-5]}'
if not os.path.exists(results_dir):
    os.mkdir(results_dir)

# create walking dir
walking_results = os.path.abspath(os.path.join(os.path.join(results_dir, 'walking')))
if not os.path.exists(walking_results):
    os.mkdir(walking_results)


def main(walking_dirs):
    start_time = time.perf_counter()
    
    # do first
    with ProcessPoolExecutor() as executor:
        executor.map(process, walking_dirs)
    # do second
    with ProcessPoolExecutor() as executor:
        executor.map(process_steps, walking_dirs)    
    # do last
    mean_step_data()
    duration = time.perf_counter() - start_time
    print(f"Computed in {duration} seconds")

def process(folder):
    input_dir = os.path.abspath(os.path.join('../', 'Python', 'walking', folder)) 
    trc_file_name = os.path.join(input_dir, 'task.trc')
    grf_mot_file_name = 'task_grf.mot'
    step_data_file_name =  'df_steps.csv'
    first_foot_file_name = 'steps.txt'

    # create trial output dir
    output_dir = os.path.abspath(os.path.join(walking_results, folder))
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    run_walking = RunAnalysesPipeline(individual_tag,model_name, model_folder,input_dir,
                                    trc_file_name, grf_mot_file_name, step_data_file_name,
                                    tempalte_dir, actuator_file, output_dir = output_dir, first_foot_file_name = first_foot_file_name)
    
    run_walking.basic()
    run_walking.run_so()
    run_walking.run_jr()

def process_steps(folder):
    muscle_disc(folder)
    extract_step_data(folder)

def muscle_disc(folder):
    ma_time_series_files = ['hip_rot_muscle_moment_arms.csv',
                        'hip_flex_muscle_moment_arms.csv',
                        'hip_add_muscle_moment_arms.csv',
                        'knee_flex_muscle_moment_arms.csv',
                        'ankle_flex_muscle_moment_arms.csv']
    path_to_time_series = os.path.join(results_dir, 'walking', folder,'muscle_moment_arms')
    write_json_to = path_to_time_series
    for table in ma_time_series_files:
        muscle_arm_discontinuity(path_to_time_series, table, write_json_to, threshold = 0.005)

def run_analyses(right_time_tuples, left_time_tuples, output_dir, folder):
    #moment arms
    #logger.info(f' Moment arms')  
    ma_time_series_files = ['hip_rot_muscle_moment_arms.csv',
                            'hip_flex_muscle_moment_arms.csv',
                            'hip_add_muscle_moment_arms.csv',
                            'knee_flex_muscle_moment_arms.csv',
                            'ankle_flex_muscle_moment_arms.csv']
    for table in ma_time_series_files:
        path_to_time_series = os.path.join(output_dir, 'muscle_moment_arms', table)
        #logger.info(f'Looking in {path_to_time_series}') 
        ma_steps = ResampleAndAverageSteps(path_to_time_series, right_time_tuples=right_time_tuples, left_time_tuples=left_time_tuples)
                
        if not ma_steps.right_df.empty:
            ma_steps.right_df.to_csv(os.path.join(output_dir, f'right_{table}'))
        if not ma_steps.left_df.empty:
            ma_steps.left_df.to_csv(os.path.join(output_dir, f'left_{table}'))

    # IK
    #logger.info('extracting steps for ' + 'IK_results.mot')
    path_to_time_series = os.path.join(output_dir, 'IK_results.mot')
    IK_steps = ResampleAndAverageSteps(path_to_time_series, right_time_tuples=right_time_tuples, left_time_tuples=left_time_tuples)

    if not IK_steps.right_df.empty:
        IK_steps.right_df.to_csv(os.path.join(output_dir, 'right_kinem.csv'))
    if not IK_steps.left_df.empty:
        IK_steps.left_df.to_csv(os.path.join(output_dir, 'left_kinem.csv'))

    IK_steps.plot_steps_one_trial(folder + ' IK', output_dir)

    # ID
    #logger.info('extracting steps for ' + 'ID_results.mot')
    path_to_time_series = os.path.join(output_dir, 'ID_results.mot')
    ID_steps = ResampleAndAverageSteps(path_to_time_series, right_time_tuples=right_time_tuples, left_time_tuples=left_time_tuples)

    if not ID_steps.right_df.empty:
        ID_steps.right_df.to_csv(os.path.join(output_dir, 'right_dynam.csv'))
    if not ID_steps.left_df.empty:
        ID_steps.left_df.to_csv(os.path.join(output_dir, 'left_dynam.csv'))

    # SO
    #logger.info('extracting steps for ' + 'SO_Results/SO_StaticOptimization_activation.sto')
    path_to_time_series = os.path.join(output_dir, 'SO_Results/SO_StaticOptimization_activation.sto')
    SO_steps = ResampleAndAverageSteps(path_to_time_series, right_time_tuples=right_time_tuples, left_time_tuples=left_time_tuples)

    if not SO_steps.right_df.empty:
        SO_steps.right_df.to_csv(os.path.join(output_dir, 'right_SO.csv'))
    if not SO_steps.left_df.empty:
        SO_steps.left_df.to_csv(os.path.join(output_dir, 'left_SO.csv'))

    # JR
    #logger.info('extracting steps for ' + 'SO_Results/JR_JointReaction_ReactionLoads.sto')
    path_to_time_series = os.path.join(output_dir, 'SO_Results/JR_JointReaction_ReactionLoads.sto')
    JR_steps = ResampleAndAverageSteps(path_to_time_series, right_time_tuples=right_time_tuples, left_time_tuples=left_time_tuples)

    if not JR_steps.right_df.empty:
        JR_steps.right_df.to_csv(os.path.join(output_dir, 'right_JR.csv'))
    if not JR_steps.left_df.empty:
        JR_steps.left_df.to_csv(os.path.join(output_dir, 'left_JR.csv'))

def extract_step_data(folder):  
    input_dir = os.path.abspath(os.path.join('../', 'Python', 'walking', folder))
    output_dir = os.path.join(walking_results, folder)
    path_to_ik_results = os.path.join(output_dir,'IK_results.mot')
    path_to_steps_data_file =  os.path.join(input_dir,'df_steps.csv')

    # extract steps
    #logger.info('\n' + 'running step extraction for ' + f'{folder}' + '\n')
    extract_steps = OneTrialSteps(path_to_ik_results, input_dir, path_to_steps_data_file, first_foot_file_name = first_foot_file_name)
    #logger.info('the first foot is '+ extract_steps.first_foot+ '\n')

    extract_steps.def_right_heel_strike()
    extract_steps.def_left_heel_strike()
    extract_steps.full_cycle() 
    
    right_time_tuples = extract_steps.right_cycle
    left_time_tuples = extract_steps.left_cycle
 
    # logger.info('right_time_tuples '+ str(len(right_time_tuples))+ '\n')
    # logger.info('right_time_tuples '+ str(right_time_tuples)+ '\n')
    # logger.info('left_time_tuples '+ str(len(left_time_tuples))+ '\n')
    # logger.info('left_time_tuples '+ str(left_time_tuples)+ '\n')

    if right_time_tuples:
        if len(right_time_tuples) > 0:
            right_time_tuples = right_time_tuples
            if left_time_tuples:
                if len(left_time_tuples) > 0:
                    left_time_tuples = left_time_tuples
                    run_analyses(right_time_tuples, left_time_tuples, output_dir, folder)
            else: 
                left_time_tuples == None
                run_analyses(right_time_tuples, left_time_tuples, output_dir, folder)
    else:
        if left_time_tuples:
            if len(left_time_tuples) > 0:
                left_time_tuples = left_time_tuples
                right_time_tuples = None
                run_analyses(right_time_tuples, left_time_tuples, output_dir, folder)
        else:  
            #logger.info('no valid step data - skip' '\n')
            pass

def mean_step_data():
    files_list = ['hip_rot_muscle_moment_arms.csv','hip_flex_muscle_moment_arms.csv',
    'hip_add_muscle_moment_arms.csv','knee_flex_muscle_moment_arms.csv',
    'ankle_flex_muscle_moment_arms.csv'] + ['kinem.csv', 'dynam.csv', 'SO.csv', 'JR.csv']

    full_file_list = []
    for name in files_list:
        for prefix in ['left_', 'right_']:
            full_file_list.append(prefix+name)

    input_path = walking_results
    output_path = os.path.abspath(os.path.join(walking_results, 'walking_results'))
    if not os.path.exists(output_path):
        os.mkdir(output_path)   

    compute_walking = ComputePersonalMeanAndSd(walking_dirs, full_file_list, input_path = input_path, output_path = output_path)
    compute_walking.average_trials(plot = True)

if __name__ == "__main__":
    main(walking_dirs)
