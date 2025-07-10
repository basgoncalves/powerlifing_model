import os
import pandas as pd

SUBJECT = 'Athlete_03'
SESSION = '22_07_06'
TRIAL_NAME = 'sq_70_EMG'
STATIC_NAME = 'static_01'

def check_path(path, create=False, isdir=False):
    """Check if a path exists and is a directory."""
    if not os.path.exists(path):        
        if create:
            try:
                os.makedirs(path)
                print("[INFO] Created directory:", path)
            except Exception as e:
                print("[ERROR] Could not create directory:", path, "Error:", e)
        else:
            print("[ERROR] Path does not exist:", path)
    if isdir and not os.path.isdir(path):
        print("[ERROR] Path is not a directory:", path)

    return path, os.path.isdir(path)

CODE,_ = check_path(os.path.dirname(__file__))
POWERLIFTING_DIR, _ = check_path(os.path.dirname(CODE), isdir=True)
SUBJECT_DIR,pathExist = check_path(os.path.join(os.path.dirname(CODE),'simulations', SUBJECT), isdir=True)
MODELS_DIR,_ = check_path(os.path.join(os.path.dirname(CODE),'models'))

if not pathExist:
    print("[ERROR] Subject path does not exist:", SUBJECT_DIR)
    raise FileNotFoundError(f"Subject path '{SUBJECT_DIR}' does not exist. Please check the configuration.")

# models paths
SCALED_MODEL = os.path.join(MODELS_DIR, 'Athlete_03_lowerBody_final.osim')
SCALED_MODEL_INCREASED_FORCE_3_TIMES = os.path.join(MODELS_DIR, 'Athlete_03_lowerBody_final_increased_3.00.osim')
MRI_MODEL = os.path.join(MODELS_DIR, 'Athlete_03_mri_based.osim')

# Modeles used for analysis
SUBJECT_MODEL_DIR = os.path.join(MODELS_DIR, 'models')
USED_MODEL = SCALED_MODEL_INCREASED_FORCE_3_TIMES
MARKERSET = os.path.join(MODELS_DIR, 'Athlete_03_markerset.xml')
ACTUATORS_MODEL = os.path.join(MODELS_DIR, 'Athlete_03_lowerBody_final_actuators.xml')

# generic setup files
GENERIC_SETUP_IK = os.path.join(CODE, 'setup_IK.xml')
GENERIC_SETUP_ID = os.path.join(CODE, 'setup_ID.xml')

# CEINMS executables paths
EXECUTABLE_DIR = os.path.join(CODE, 'executables')
CEINMS_PATH = os.path.join(EXECUTABLE_DIR, 'CEINMS.exe')
CEINMS_OPTIMISE_EXE = os.path.join(EXECUTABLE_DIR, 'CEINMSoptimise.exe')
CEINMS_CALIBRATION_EXE = os.path.join(EXECUTABLE_DIR, 'ceinms-nn-calibrate.exe')

GEOMETRY_PATH = os.path.join(SUBJECT_DIR, 'Geometry')

# Session specific paths
SESSION_DIR, sessionExists = check_path(os.path.join(SUBJECT_DIR, SESSION), create=False, isdir=True)
CEINMS_EXCITATION_MAPPING = os.path.join(SESSION_DIR, 'excitationGenerator.xml')
CEINMS_SETUP_CALIBRATION = os.path.join(SESSION_DIR, 'calibrationSetup_ceinms-nn_hybrid.xml')

OUTPUT_HYBRID_CALIBRATION,_ = check_path(os.path.join(SESSION_DIR, 'calibration_hybrid'), create=True, isdir=True)
OUPUT_DRIVEN_CALIBRATION,_ = check_path(os.path.join(SESSION_DIR, 'calibration_driven'), create=True, isdir=True)

UNCALIBRATED_MODEL_PATH = os.path.join(SESSION_DIR, 'subjectUncalibrated.xml')
CALIBRATED_MODEL_PATH = os.path.join(SESSION_DIR, 'subjectCalibrated_hybrid.xml')

TRIAL_CALIBRATION_PATH = os.path.join(SESSION_DIR, TRIAL_NAME)

# Trial specific paths
STATIC_PATH = os.path.join(SESSION_DIR, STATIC_NAME)
TRIAL_PATH = os.path.join(SESSION_DIR, TRIAL_NAME)
C3D_PATH = os.path.join(TRIAL_PATH, 'c3dfile.c3d')
EVENTS_PATH = os.path.join(TRIAL_PATH, 'c3dfile.csv')
MARKERS_TRC = os.path.join(TRIAL_PATH, 'marker_experimental.trc')
GRF_MOT = os.path.join(TRIAL_PATH, 'grf.mot')
EMG_MOT = os.path.join(TRIAL_PATH, 'EMG_filtered.sto')
GRF_XML = os.path.join(TRIAL_PATH, 'externalloads.xml')

SETUP_IK = os.path.join(TRIAL_PATH, 'setup_IK.xml')
SETUP_ID = os.path.join(TRIAL_PATH, 'setup_ID.xml')
SETUP_SO = os.path.join(TRIAL_PATH, 'setup_SO.xml')

IK_OUTPUT = os.path.join(TRIAL_PATH, 'joint_angles.mot')
ID_OUTPUT = os.path.join(TRIAL_PATH, 'inverse_dynamics.sto')
MA_OUTPUT = os.path.join(TRIAL_PATH, 'muscleAnalysis')
SO_OUTPUT = os.path.join(TRIAL_PATH)

RESULTS_OPTIMISE = os.path.join(TRIAL_PATH, 'Optimised')
RESULTS_EXE = os.path.join(TRIAL_PATH, 'Output')

SETUP_EXECUTION_PATH = os.path.join(TRIAL_PATH, 'setup_ceinms_exe.xml')
SETUP_OPTIMISE_PATH = os.path.join(TRIAL_PATH, 'setup_optimise_ceinms.xml')

# get trial time range from the marker file if not provided

events = pd.read_csv(EVENTS_PATH, index_col=0, header=None)
TIME_RANGE = [events.iloc[0, 0], events.iloc[1, 0]]

