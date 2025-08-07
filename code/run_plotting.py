import os
import compare_all_files_trials
import utils
import paths


analysis = paths.Analysis()
settings = paths.Settings()
basedir = paths.SIMULATION_DIR

subject_list = analysis.subject_list
session_name = '22_06_07'
trial_list = settings.TRIAL_TO_ANALYSE
trial_list = [
    os.path.join(basedir,subject_list[0],session_name, trial_list[0], 'joint_angles.mot')
]
