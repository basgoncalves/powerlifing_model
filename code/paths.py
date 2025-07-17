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
#          setup_IK.xml
#          setup_ID.xml 
#          setup_MA.xml
#          setup_SO.xml
#          externalloads.xml    
#          ...
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

PATHS_DIR = os.path.dirname(__file__)
SUBJECT = 'Athlete_03'
SESSION = '22_07_06'
TRIAL_NAME = 'sq_70_EMG'
STATIC_NAME = 'static_01'
EMG_NORMALISE_LIST = ['sq_70_MRI','sq_90_MRI','sq_90_MRI']

def save_self():
    """
    Save the current state of the paths module.
    This is useful for debugging and ensuring that the paths are correctly set.
    """
    with open(PATHS_DIR, 'w') as f:
        f.write(f"SUBJECT = '{SUBJECT}'\n")
        f.write(f"SESSION = '{SESSION}'\n")
        f.write(f"TRIAL_NAME = '{TRIAL_NAME}'\n")
        f.write(f"STATIC_NAME = '{STATIC_NAME}'\n")
        f.write(f"EMG_NORMALISE_LIST = {EMG_NORMALISE_LIST}\n")

def set_subject(subject):
    """
    Set the subject for the paths.
    
    Parameters:
        subject (str): Name of the subject.
    """
    global SUBJECT
    SUBJECT = subject


# CEINMS settings
DOFs = ['hip_flexion_l', 'hip_flexion_r', 
        'hip_adduction_l', 'hip_adduction_r', 
        'hip_rotation_l', 'hip_rotation_r', 
        'knee_angle_l', 'knee_angle_r'
        'ankle_angle_l', 'ankle_angle_r']


Muscle_Groups = { 'Adductors': ['addbrev_r','addlong_r','addmagDist_r','addmagIsch_r','addmagMid_r','addmagProx_r','grac_r'],
            'Hamstrings': ['bflh_r','semimem_r','semiten_r','bfsh_r'],
            'Gluteus maximus':['glmax1_r','glmax2_r','glmax3_r'],
            'Gluteus medius':['glmed1_r','glmed2_r','glmed3_r'],
            'Gluteus minimus':['glmin1_r','glmin2_r','glmin3_r'],
            'Hip flexors':['sart_r','recfem_r','tfl_r','iliacus_r','psoas_r'],            
            'Triceps Surae':['soleus_r','gaslat_r','gasmed_r'],
            'Vasti':['vasint_r','vaslat_r','vasmed_r']
            }

JCF_Groups = {'Hip': ['hip_r_on_femur_r_in_femur_r_fx', 'hip_r_on_femur_r_in_femur_r_fy', 'hip_r_on_femur_r_in_femur_r_fz'],
              'Knee': ['walker_knee_r_on_tibia_r_in_tibia_r_fx', 'walker_knee_r_on_tibia_r_in_tibia_r_fy', 'walker_knee_r_on_tibia_r_in_tibia_r_fz'],
              'Ankle': ['ankle_r_on_talus_r_in_talus_r_fx', 'ankle_r_on_talus_r_in_talus_r_fy', 'ankle_r_on_talus_r_in_talus_r_fz']}

EMG_muscle_mapping = {
    # Left Leg Muscles
    'Voltage_EMG1_vast_lat_l': ['vasint_l', 'vaslat_l', 'vasmed_l'],
    'Voltage_EMG3_rect_fem_l': ['iliacus_l', 'psoas_l', 'recfem_l', 'sart_l', 'tfl_l'],
    'Voltage_EMG5_bic_fem_l': ['bflh_l', 'bfsh_l', 'semimem_l', 'semiten_l'],
    'Voltage_EMG7_glut_max_l': ['glmax1_l', 'glmax2_l', 'glmax3_l', 'glmed1_l', 'glmed2_l', 'glmed3_l', 'glmin1_l', 'glmin2_l', 'glmin3_l'],
    'Voltage_EMG9_gast_med_l': ['gaslat_l', 'gasmed_l', 'soleus_l'],
    'Voltage_EMG13_add_mag_l': ['addbrev_l', 'addlong_l', 'addmagDist_l', 'addmagIsch_l', 'addmagMid_l', 'addmagProx_l', 'grac_l'],

    # Right Leg Muscles
    'Voltage_EMG2_vast_lat_r': ['vasint_r', 'vaslat_r', 'vasmed_r'],
    'Voltage_EMG4_rect_fem_r': ['iliacus_r', 'psoas_r', 'recfem_r', 'sart_r', 'tfl_r'],
    'Voltage_EMG6_bic_fem_r': ['bflh_r', 'bfsh_r', 'semimem_r', 'semiten_r'],
    'Voltage_EMG8_glut_max_r': ['glmax1_r', 'glmax2_r', 'glmax3_r', 'glmed1_r', 'glmed2_r', 'glmed3_r', 'glmin1_r', 'glmin2_r', 'glmin3_r'],
    'Voltage_EMG10_gast_med_r': ['gaslat_r', 'gasmed_r', 'soleus_r'],
    'Voltage_EMG14_add_mag_r': ['addbrev_r', 'addlong_r', 'addmagDist_r', 'addmagIsch_r', 'addmagMid_r', 'addmagProx_r', 'grac_r']
}

plot_settings = {'Groups':
                        {'SO_StaticOptimization_force': Muscle_Groups,
                        'Analyse_JRA_ReactionLoads': JCF_Groups,
                        'SO_StaticOptimization_force_normalised': Muscle_Groups,
                        'SO_StaticOptimization_activation': EMG_muscle_mapping},
                'Summary': 
                    {'SO_StaticOptimization_force': 'Sum', 
                     'SO_StaticOptimization_force': 'mean', 
                     'Analyse_JRA_ReactionLoads': '3dsum'}
                }


# Code and executables paths
CODE,_ = utils.check_path(os.path.dirname(__file__))
SETUP_DIR = os.path.join(CODE, 'SetupFiles\Purzel')

POWERLIFTING_DIR,_ = utils.check_path(os.path.dirname(CODE), isdir=True)
SIMULATION_DIR = os.path.join(POWERLIFTING_DIR, 'simulations')
RESULTS_DIR = os.path.join(POWERLIFTING_DIR, 'results', SUBJECT)

# models paths
MODELS_DIR,_ = utils.check_path(os.path.join(os.path.dirname(CODE),'models'))
SCALED_MODEL = os.path.join(MODELS_DIR, f'{SUBJECT}_linearly_scaled.osim')
SCALED_MODEL_INCREASED_FORCE = os.path.join(MODELS_DIR, f'{SUBJECT}_linearly_scaled_increased_20.00.osim')
MRI_MODEL = os.path.join(MODELS_DIR, f'{SUBJECT}_mri_scaled.osim')
MRI_MODEL_INCREASED_FORCE = os.path.join(MODELS_DIR, f'{SUBJECT}_mri_scaled_increased_20.00.osim')

SCALED_MODEL_SCALED_MASSES = os.path.join(MODELS_DIR, SCALED_MODEL.replace('.osim', '_scaledMasses.osim'))
MRI_MODEL_SCALED_MASSES = os.path.join(MODELS_DIR, MRI_MODEL.replace('.osim', '_scaledMasses.osim'))

CATELI_MODEL = os.path.join(MODELS_DIR, f'{SUBJECT}_Catelli_final.osim')
##################################  Models used for analysis #######################################################3
SUBJECT_MODEL_DIR = os.path.join(MODELS_DIR, 'models')

if TRIAL_NAME.lower().__contains__('mri'):  # Edit model paths below
    USED_MODEL = MRI_MODEL_SCALED_MASSES
else:
    USED_MODEL = SCALED_MODEL_SCALED_MASSES
    
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
GENERIC_SETUP_JRA = os.path.join(GENREIC_SETUP_DIR, 'setup_JRA.xml')

GENERIC_CEINMS_SETUP_OPTIMISE = os.path.join(GENREIC_SETUP_DIR, 'setup_ceinms_optimise.xml')
GENERIC_CEINMS_CFG_OPTIMISE = os.path.join(GENREIC_SETUP_DIR, 'ceinms_cfg_optimise.xml')
GENERIC_CEINMS_INPUT_DATA = os.path.join(GENREIC_SETUP_DIR, 'inputData.xml')
GENERIC_CEINMS_RUN_OPTIMISE_BAT = os.path.join(GENREIC_SETUP_DIR, 'run_ceinms_nn_optimise.bat')

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
EMG_MOT_NORMALISED = os.path.join(TRIAL_DIR, 'EMG_filtered_normalised.sto')
GRF_XML = os.path.join(TRIAL_DIR, 'externalloads.xml')

ACTUATORS_SO = os.path.join(TRIAL_DIR, 'actuators_so.xml')

SETUP_IK = os.path.join(TRIAL_DIR, 'setup_IK.xml')
SETUP_ID = os.path.join(TRIAL_DIR, 'setup_ID.xml')
SETUP_MA = os.path.join(TRIAL_DIR, 'setup_MA.xml')
SETUP_SO = os.path.join(TRIAL_DIR, 'setup_SO.xml')
SETUP_JRA = os.path.join(TRIAL_DIR, 'setup_JRA.xml')

IK_OUTPUT = os.path.join(TRIAL_DIR, 'joint_angles.mot')
ID_OUTPUT = os.path.join(TRIAL_DIR, 'inverse_dynamics.sto')
MA_OUTPUT = os.path.join(TRIAL_DIR, 'muscleAnalysis')
SO_OUTPUT = os.path.join(TRIAL_DIR)
FORCES_OUTPUT = os.path.join(SO_OUTPUT, 'SO_StaticOptimization_force.sto')

JRA_OUTPUT = os.path.join(TRIAL_DIR, 'Analyse_JRA_ReactionLoads.sto')

CEINMS_INPUT_DATA = os.path.join(TRIAL_DIR, os.path.basename(GENERIC_CEINMS_INPUT_DATA))
CEINMS_CFG_OPTIMISE = os.path.join(TRIAL_DIR, os.path.basename(GENERIC_CEINMS_CFG_OPTIMISE))
CEINMS_SETUP_OPTIMISE = os.path.join(TRIAL_DIR, os.path.basename(GENERIC_CEINMS_SETUP_OPTIMISE))

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
    print(" \n")
    # CEINMS paths
    print('CEINMS_PATH:', CEINMS_PATH)
    print('CEINMS_EXCITATION_MAPPING:', CEINMS_EXCITATION_MAPPING)
    print('CEINMS_INPUT_DATA:', CEINMS_INPUT_DATA)
    print('CEINMS_CFG_CALIBRATION:', CEINMS_CFG_CALIBRATION)
    print('CEINMS_SETUP_CALIBRATION:', CEINMS_SETUP_CALIBRATION)
    print('CEINMS_CFG_OPTIMISE:', CEINMS_CFG_OPTIMISE)
    print('CEINMS_SETUP_OPTIMISE:', CEINMS_SETUP_OPTIMISE)
    
    print('CEINMS_CALIBRATED_MODEL:', CEINMS_CALIBRATED_MODEL)
    print('CEINMS_UNCALIBRATED_MODEL:', CEINMS_UNCALIBRATED_MODEL)
    print('CEINMS_RESULTS_OPTIMISE_DIR:', CEINMS_RESULTS_OPTIMISE_DIR)
    
    
    
    
    
    time.sleep(1)  # Optional: wait for a second before printing
    

if __name__ == "__main__":
    print_settings()  # Call the print function to display paths

# END