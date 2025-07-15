import os
import shutil
import time
import pandas as pd
import utils

# Folder stuctures should be: 
# powerlifitng_model
#   code/
#     setupFiles/
#       Rajagopal/
#       Purzel/
#     executables/
#       CEINMS.exe
#       CEINMSoptimise.exe
#       ceinms-nn-calibrate.exe
#     paths.py
#     ceinms_muscle_groups_to_unCalibrated_model.py
#   models/
#     Athlete_03_linearly_scaled.osim
#     Athlete_03_mri_scaled.osim
#     Athlete_03_markerset.xml
#   simulations/
#     Athlete_03/
#       22_07_06/
#         sq_70_MRI/
#           c3dfile.c3d
#           events.csv
#           marker_experimental.trc
#           grf.mot
#           EMG_filtered.sto
#           externalloads.xml

SUBJECT = 'Athlete_03'
SESSION = '22_07_06'
TRIAL_NAME = 'sq_75_MRI'
STATIC_NAME = 'static_01'

# CEINMS settings
DOFs = ['hip_flexion_l', 'hip_flexion_r', 
        'hip_adduction_l', 'hip_adduction_r', 
        'hip_rotation_l', 'hip_rotation_r', 
        'knee_angle_l', 'knee_angle_r'
        'ankle_angle_l', 'ankle_angle_r']

# Code and executables paths
CODE,_ = utils.check_path(os.path.dirname(__file__))
POWERLIFTING_DIR,_ = utils.check_path(os.path.dirname(CODE), isdir=True)
SETUP_DIR = os.path.join(CODE, 'SetupFiles\Rajagopal')
SIMULATION_DIR = os.path.join(CODE, 'simulations')

# models paths
MODELS_DIR,_ = utils.check_path(os.path.join(os.path.dirname(CODE),'models'))
SCALED_MODEL = os.path.join(MODELS_DIR, f'{SUBJECT}_linearly_scaled.osim')
SCALED_MODEL_INCREASED_FORCE_3_TIMES = os.path.join(MODELS_DIR, '{SUBJECT}_lowerBody_final_increased_3.00.osim')
MRI_MODEL = os.path.join(MODELS_DIR, 'Athlete_03_mri_scaled.osim')

# Models used for analysis
SUBJECT_MODEL_DIR = os.path.join(MODELS_DIR, 'models')

if TRIAL_NAME.lower().__contains__('mri'):
    USED_MODEL = MRI_MODEL
else:
    USED_MODEL = SCALED_MODEL
    
MARKERSET = os.path.join(MODELS_DIR, 'Athlete_03_markerset.xml')
GEOMETRY_PATH = os.path.join(MODELS_DIR, 'Geometry')

# generic setup files
GENREIC_SETUP_DIR = os.path.join(CODE, 'SetupFiles\\Purzel')
GENERIC_GRF_XML = os.path.join(GENREIC_SETUP_DIR, 'externalloads.xml')
GENERIC_SETUP_IK = os.path.join(GENREIC_SETUP_DIR, 'setup_IK.xml')
GENERIC_SETUP_ID = os.path.join(GENREIC_SETUP_DIR, 'setup_ID.xml')
GENERIC_SETUP_MA = os.path.join(GENREIC_SETUP_DIR, 'setup_MA.xml')
GENERIC_ACTUATORS_SO = os.path.join(GENREIC_SETUP_DIR, 'actuators_so.xml')
GENERIC_SETUP_SO = os.path.join(GENREIC_SETUP_DIR, 'setup_SO.xml')

# CEINMS executables paths
EXECUTABLE_DIR = os.path.join(CODE, 'executables')
CEINMS_PATH = os.path.join(EXECUTABLE_DIR, 'CEINMS.exe')
CEINMS_OPTIMISE_EXE = os.path.join(EXECUTABLE_DIR, 'CEINMSoptimise.exe')
CEINMS_CALIBRATION_EXE = os.path.join(EXECUTABLE_DIR, 'ceinms-nn-calibrate.exe')

# Subject specific paths
SUBJECT_DIR,pathExist = utils.check_path(os.path.join(os.path.dirname(CODE),'simulations', SUBJECT), isdir=True)
if not pathExist:
    print("[ERROR] Subject path does not exist:", SUBJECT_DIR)
    raise FileNotFoundError(f"Subject path '{SUBJECT_DIR}' does not exist. Please check the configuration.")

# Session specific paths
SESSION_DIR, sessionExists = utils.check_path(os.path.join(SUBJECT_DIR, SESSION), create=False, isdir=True)
if not sessionExists:
    print("[ERROR] Session path does not exist:", SESSION_DIR)
    raise FileNotFoundError(f"Session path '{SESSION_DIR}' does not exist. Please check the configuration.")

TRIAL_LIST = os.listdir(SESSION_DIR)
CEINMS_EXCITATION_MAPPING = os.path.join(SESSION_DIR, 'excitationGenerator.xml')
CEINMS_SETUP_CALIBRATION = os.path.join(SESSION_DIR, 'calibrationSetup_ceinms-nn_hybrid.xml')
CEINMS_CFG_CALIBRATION = os.path.join(SESSION_DIR, 'calibrationCfg_ceinms-nn_hybrid.xml')

OUTPUT_HYBRID_CALIBRATION,_ = utils.check_path(os.path.join(SESSION_DIR, 'calibration_hybrid'), create=True, isdir=True)
OUPUT_DRIVEN_CALIBRATION,_ = utils.check_path(os.path.join(SESSION_DIR, 'calibration_driven'), create=True, isdir=True)

CEINMS_UNCALIBRATED_MODEL = os.path.join(SESSION_DIR, 'subjectUncalibrated.xml')
CEINMS_CALIBRATED_MODEL = os.path.join(SESSION_DIR, 'subjectCalibrated_hybrid.xml')

CEINMS_TRIAL_CALIBRATION_DIR = os.path.join(SESSION_DIR, TRIAL_NAME)

# Trial specific paths
STATIC_DIR = os.path.join(SESSION_DIR, STATIC_NAME)
TRIAL_DIR = os.path.join(SESSION_DIR, TRIAL_NAME)
C3D = os.path.join(TRIAL_DIR, 'c3dfile.c3d')
EVENTS = os.path.join(TRIAL_DIR, 'events.csv')
MARKERS_TRC = os.path.join(TRIAL_DIR, 'marker_experimental.trc')
GRF_MOT = os.path.join(TRIAL_DIR, 'grf.mot')
EMG_MOT = os.path.join(TRIAL_DIR, 'EMG_filtered.sto')
GRF_XML = os.path.join(TRIAL_DIR, 'externalloads.xml')

ACTUATORS_SO = os.path.join(MODELS_DIR, 'actuators_so.xml')

SETUP_IK = os.path.join(TRIAL_DIR, 'setup_IK.xml')
SETUP_ID = os.path.join(TRIAL_DIR, 'setup_ID.xml')
SETUP_MA = os.path.join(TRIAL_DIR, 'setup_MA.xml')
SETUP_SO = os.path.join(TRIAL_DIR, 'setup_SO.xml')

IK_OUTPUT = os.path.join(TRIAL_DIR, 'joint_angles.mot')
ID_OUTPUT = os.path.join(TRIAL_DIR, 'inverse_dynamics.sto')
MA_OUTPUT = os.path.join(TRIAL_DIR, 'muscleAnalysis')
SO_OUTPUT = os.path.join(TRIAL_DIR)
FORCES_OUTPUT = os.path.join(SO_OUTPUT, '_StaticOptimization_force.sto')

CEINMS_INPUT_DATA = os.path.join(TRIAL_DIR, 'inputData.xml')
CEINMS_CFG_OPTIMISE = os.path.join(TRIAL_DIR, 'ceinms_cfg_optimise.xml')

CEINMS_SETUP_EXECUTION = os.path.join(TRIAL_DIR, 'setup_ceinms_exe.xml')
CEINMS_SETUP_OPTIMISE = os.path.join(TRIAL_DIR, 'setup_optimise_ceinms.xml')

CEINMS_RESULTS_OPTIMISE_DIR = os.path.join(TRIAL_DIR, 'Optimised')
CEINMS_RESULTS_EXE_DIR = os.path.join(TRIAL_DIR, 'Output')

# get trial time range from the marker file if not provided
if not os.path.exists(EVENTS):
    # create a dummy events file with start and end times
    events = pd.DataFrame([[None, None], [None, None]], columns=['General_start', 'General_start'])
    events.to_csv(EVENTS, index=False, header=False)
    print(f"Dummy events file created at {EVENTS} with start and end times.")
    
events = pd.read_csv(EVENTS, index_col=0, header=None)
TIME_RANGE = [events.iloc[0, 0], events.iloc[1, 0]]
if any(pd.isna(TIME_RANGE)):
    print(f"Warning: Time range in {EVENTS} is not set. Using default time range [0, 1].")
    
def print_settings():
    """Print the paths for debugging."""
    print("CODE:", CODE)
    print("POWERLIFTING_DIR:", POWERLIFTING_DIR)
    print("USED_MODEL:", USED_MODEL)
    print("MARKERSET:", MARKERSET)
    print("ACTUATORS_MODEL:", ACTUATORS_SO)
    print("GEOMETRY_PATH:", GEOMETRY_PATH)
    print("SUBJECT_DIR:", SUBJECT_DIR)
    print("SESSION_DIR:", SESSION_DIR)
    print("TRIAL_DIR:", TRIAL_DIR)
    print("C3D:", C3D)
    print("EVENTS:", EVENTS)
    print("MARKERS_TRC:", MARKERS_TRC)
    print("GRF_MOT:", GRF_MOT)
    print("EMG_MOT:", EMG_MOT)
    print("GRF_XML:", GRF_XML)
    
    time.sleep(1)  # Optional: wait for a second before printing
    

if __name__ == "__main__":
    print_settings()  # Call the print function to display paths

# END