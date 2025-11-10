import os
from pathlib import Path

'''
For this to work folder structure is assumed:
powerlifing_model/
    code/
        settings.py
    models/
        subject1/
            session1/
                model_name 
        subject2/
    simulations/
        subject1/
            session1/
                trial1/
                trial2/
            session2/
        subject2/
        ...
    results/

'''

SUBJECTS_TO_ANALYSE =  ['Running_009'] # 'Athlete_03_MRI_BG','Athlete_03_MRI_Katya'['Katya_01','Athlete_03', 'Athlete_04', 'Athlete_05', 'Athlete_06', 'Athlete_07']

SESSIONS_TO_ANALYSE = ['session1'] # '22_07_06' \25_03_31 

TRIALS_TO_ANALYSE =  ['Walking_04', 'Walking_05',
                      'Squat_bw_01', 'Squat_bw_02',
                      'Squat_bw_03',
                      'Squat_bar_02', 'Squat_bar_03',
                      'Squat_bar_04',] # [Squat_bw_01,'sq_80','sq_90','dl_70','dl_75','dl_80','dl_85','dl_90']#['sq_70','sq_75','sq_80','sq_85','sq_90'] #


TRIALS_TO_ANALYSE = ['runA1'] # , 'Walking_02','Walking_03', 'Walking_04', 'Walking_05'

CEINMS_CALIBRATION_TRIALS = ['runA1'] 

MODEL_NAME = 'model_scaled_increasedForce3.osim'

# Check local location of this module
MODULE_DIR = os.path.dirname(__file__)

# For new projects, create a new folder in SetupFiles and update the path here 
SETUP_DIR = os.path.join(MODULE_DIR, 'SetupFiles\Purzel')
POWERLIFTING_DIR = os.path.dirname(MODULE_DIR)
MODELS_DIR = os.path.join(POWERLIFTING_DIR, 'models')

SIMULATIONS_DIR = os.path.join(POWERLIFTING_DIR, 'simulations')
RESULTS_DIR = os.path.join(POWERLIFTING_DIR, 'results')

CEINMS_DIR = os.path.join(MODULE_DIR, 'executables')
CEINMS_EXE = os.path.join(CEINMS_DIR, 'CEINMS.exe')
CEINMS_OPTIMISE_EXE = os.path.join(CEINMS_DIR, 'CEINMSoptimise.exe')
CEINMS_CALIBRATION_EXE = os.path.join(CEINMS_DIR, 'ceinms-nn-calibrate.exe')   

SUBJECT_LIST = [subject for subject in os.listdir(SIMULATIONS_DIR) if os.path.isdir(os.path.join(SIMULATIONS_DIR, subject))]

class Inputs:
    def __init__(self, parentdir=None):
        
        self.SetupFiles = SETUP_DIR
        self.MODEL = os.path.join(MODELS_DIR, 'subject', 'session', MODEL_NAME)
        self.C3D = 'c3dfile.c3d'
        self.EMG_RAW = 'emg.mot'
        self.EMG_FILTERED = 'EMG_filtered.sto'
        self.EMG_NORMALISED = 'EMG_filtered_normalised.sto'
        self.GRF_MOT = 'grf.mot'
        self.MARKERS = 'marker_experimental.trc'
        self.EVENTS = 'events.csv'
        
        # setups 
        self.setupIK = 'setup_IK.xml'
        self.setupGRF = 'GRF.xml'   
        self.setupID = 'setup_ID.xml'
        self.setupMA = 'setup_MA.xml'
        self.ACTUATORS_SO = 'actuators_so.xml' 
        self.setupSO = 'setup_SO.xml'
        self.JRA_FORCES = 'SO_StaticOptimization_force.sto'
        self.setupJRA = 'setup_JRA.xml'
        
        self.CEINMS_EXCITATIONS = self.EMG_NORMALISED
        self.CEINMS_UNCALIBRATED_MODEL= '..\subjectUncalibrated.xml'
        self.CEINMS_CALIBRATED_MODEL = '..\subjectCalibrated.xml'
        self.CEINMS_CALIBRATION_CFG = '..\calibrationCfg.xml'
        self.CEINMS_CALIBRATION_SETUP = '..\calibrationSetup.xml'
        self.CEINMS_INPUT_DATA = 'inputData.xml'
        self.CEINMS_EXCITATION_GENERATOR = '..\excitationGenerator.xml'
        
        self.CEINMS_OPTIMISE_SETUP = 'ceinms_setup_optimise.xml'
        self.CEINMS_OPTIMISE_CFG = 'ceinms_cfg_optimise.xml'
        
        self.CEINMS_EXE_SETUP = 'ceinms_setup.xml'
        
        self.IK = 'joint_angles.mot'
        self.ID = 'inverse_dynamics.sto'
        self.MA = 'muscleAnalysis'
        self.SO_forces = 'SO_StaticOptimization_force.sto'
        self.SO_activations = 'SO_StaticOptimization_activation.sto'
        self.JRA = 'Analyse_JRA_ReactionLoads.sto'
        
        self.CEINMS_CALIBRATION_DIR = '..\calibrationOutput'
        self.CEINMS_OPTIMISATION_DIR = 'Optimised'
        self.CEINMS_EXE_DIR = 'Output'
        
        self.JRA_FORCES_CEINMS = os.path.join(self.CEINMS_OPTIMISATION_DIR,
                                              'MuscleForces.sto')
        self.JRA_CEINMS = 'Analyse_JRA_ReactionLoads_CEINMS.sto'
        
        if parentdir:
            for attr, filename in self.__dict__.items():
                filepath = os.path.join(parentdir, filename)
                relpath = os.path.relpath(filepath, parentdir)
                setattr(self, attr, relpath)
                

    def check(self, parentdir):
        fileExist = {}
        for attr, filename in self.__dict__.items():
            filepath = os.path.join(parentdir, filename)
            
            if not os.path.exists(filepath):
                print(f'Warning: Input file {filename} not found in {parentdir}')
                fileExist[attr] = False
            else:
                fileExist[attr] = True
        
        return fileExist    
            
class CEINMSParameters:
    def __init__(self):
        self.hybridCalibration = 'true'
        self.numberOfSynergies = 8
        self.betaMin = 1
        self.betaMax = 10
        self.betaDelta = 2
        self.gammaMin = 1
        self.gammaMax = 300
        self.gammaDelta = 50
        
        self.Target_Muscles = ['all']  # e.g., ['glmax1_r','glmax2_r','glmax3_r']
        
        self.Objective_Functions = []
        self.Objective_Functions.append({
            'name': 'MomentError',
            'targets': 'all',
            'weight': 1
        })
        self.Objective_Functions.append({
            'name': 'Penalty',
            'targetType': 'normalisedFibreLength',
            'weight': 10,
            'exponent': 2,
            'range': '0.5 1.5'
        })
        self.Objective_Functions.append({
            'name': 'Penalty',
            'targetType': 'tendonStrain',
            'weight': 1000,
            'exponent': 2,
            'range': '0. 0.5'
        })
        self.Objective_Functions.append({
            'name': 'ExcitationsSquared',
            'weight': 1
        })
        self.Objective_Functions.append({
            'name': 'SynergyExtraction',
            'mseWeight': 100,
            'range': '0. 1.',
            'rangeExponent': 2,
            'rangeWeight': 1000
        })
        
class Execute:
    ''' Logics for which analyses to execute '''
    def __init__(self):
               
        self.reset = False
        self.create_settings_xml = False
        self.INCREASE_MUSCLE_FORCE = False
        self.SCALE_FACTOR = 3
        self.exportC3D = False
        self.IK = False
        self.ID = False
        self.MA = False
        self.MOMENT_ARMS = False
        self.SO = False
        self.JRA = True
        self.JRA_CEINMS = True
        
        self.EMG_NORMALISE = False
        self.SCALE_EMG = False
        self.EMG_SCALE_FACTOR = 0.7
        
        self.CREATE_CEINMS_FILES = False
        self.CREATE_CEINMS_MODEL = False
        
        self.CEINMS_CALIBRATION = False
        self.CEINMS_CALIBRATION_PLOTS = False
        
        self.CEINMS_OPTIMISATION = False
        self.CEINMS_EXE = False
        
        self.CREATE_PLOTS = False
        
        self.push_to_git = False
               

DOFs = ['hip_flexion_l', 'hip_flexion_r',
                'hip_adduction_l', 'hip_adduction_r',
                'hip_rotation_l', 'hip_rotation_r',
                'knee_angle_l', 'knee_angle_r',
                'ankle_angle_l', 'ankle_angle_r']

DOFs_moments = {'hip_flexion_r': 'hip_flexion_r_moment',
                'hip_adduction_r': 'hip_adduction_r_moment',
                'hip_rotation_r': 'hip_rotation_r_moment',
                'knee_angle_r': 'knee_angle_r_moment',
                'ankle_angle_r': 'ankle_angle_r_moment',
                'hip_flexion_l': 'hip_flexion_l_moment',
                'hip_adduction_l': 'hip_adduction_l_moment',
                'hip_rotation_l': 'hip_rotation_l_moment',
                'knee_angle_l': 'knee_angle_l_moment',
                'ankle_angle_l': 'ankle_angle_l_moment'}

Muscle_Groups = { 'R Adductors': ['addbrev_r','addlong_r','addmagDist_r','addmagIsch_r','addmagMid_r','addmagProx_r','grac_r'],
    'R Hamstrings': ['bflh_r','semimem_r','semiten_r','bfsh_r'],
    'R Gluteus maximus':['glmax1_r','glmax2_r','glmax3_r'],
    'R Gluteus medius':['glmed1_r','glmed2_r','glmed3_r'],
    'R Gluteus minimus':['glmin1_r','glmin2_r','glmin3_r'],
    'R Hip flexors':['sart_r','recfem_r','tfl_r','iliacus_r','psoas_r'],            
    'R Triceps Surae':['soleus_r','gaslat_r','gasmed_r'],
    'R Vasti':['vasint_r','vaslat_r','vasmed_r'],
    'L Adductors': ['addbrev_l','addlong_l','addmagDist_l','addmagIsch_l','addmagMid_l','addmagProx_l','grac_l'],
    'L Hamstrings': ['bflh_l','semimem_l','semiten_l','bfsh_l'],
    'L Gluteus maximus':['glmax1_l','glmax2_l','glmax3_l'],
    'L Gluteus medius':['glmed1_l','glmed2_l','glmed3_l'],
    'L Gluteus minimus':['glmin1_l','glmin2_l','glmin3_l'],
    'L Hip flexors':['sart_l','recfem_l','tfl_l','iliacus_l','psoas_l'],
    'L Triceps Surae':['soleus_l','gaslat_l','gasmed_l'],
    'L Vasti':['vasint_l','vaslat_l','vasmed_l']
    }

# To match Pürzel, A. et al. (2025) Scand. J. Med. Sci. Sports 35
Muscle_Groups = {'R Gluteus maximus':['glmax1_r','glmax2_r','glmax3_r'],
                        'R Gluteus medius':['glmed1_r','glmed2_r','glmed3_r'],
                        'R Gluteus minimus':['glmin1_r','glmin2_r','glmin3_r'], 
                        'R Adductor Magnus': ['addmagDist_r','addmagIsch_r','addmagMid_r','addmagProx_r'],
                        'R Biceps Femoris': ['bflh_r','bfsh_r'],
                        'R Semimembranosus': ['semimem_r'],
                        'R Semitendinosus': ['semiten_r'],
                        'R Rectus Femoris': ['recfem_r'],
                        'R Vasti':['vasint_r','vaslat_r','vasmed_r'],
                        'R Gastrocnemius': ['gaslat_r','gasmed_r'],
                        'R Soleus': ['soleus_r'],
                        'L Gluteus maximus':['glmax1_l','glmax2_l','glmax3_l'],
                        'L Gluteus medius':['glmed1_l','glmed2_l','glmed3_l'],
                        'L Gluteus minimus':['glmin1_l','glmin2_l','glmin3_l'],
                        'L Adductor Magnus': ['addmagDist_l','addmagIsch_l','addmagMid_l','addmagProx_l'],
                        'L Biceps Femoris': ['bflh_l','bfsh_l'],
                        'L Semimembranosus': ['semimem_l'],
                        'L Semitendinosus': ['semiten_l'],
                        'L Rectus Femoris': ['recfem_l'],
                        'L Vasti':['vasint_l','vaslat_l','vasmed_l'],
                        'L Gastrocnemius': ['gaslat_l','gasmed_l'],
                        'L Soleus': ['soleus_l']}

Muscle_Groups = {'R Gluteus maximus':['glmax1_r','glmax2_r','glmax3_r'],
                        'R Gluteus medius':['glmed1_r','glmed2_r','glmed3_r'],
                        'R Gluteus minimus':['glmin1_r','glmin2_r','glmin3_r'], 
                        'R Adductor Magnus': ['addmagDist_r','addmagIsch_r','addmagMid_r','addmagProx_r'],
                        'R Biceps Femoris': ['bflh_r','bfsh_r'],
                        'R Semimembranosus': ['semimem_r'],
                        'R Semitendinosus': ['semiten_r'],
                        'R Rectus Femoris': ['recfem_r'],
                        'R Vasti':['vasint_r','vaslat_r','vasmed_r'],
                        'R Gastrocnemius': ['gaslat_r','gasmed_r'],
                        'R Soleus': ['soleus_r']}

JCF_Groups = {'Hip': ['hip_r_on_femur_r_in_femur_r_fx', 'hip_r_on_femur_r_in_femur_r_fy', 'hip_r_on_femur_r_in_femur_r_fz'],
            'Knee': ['walker_knee_r_on_tibia_r_in_tibia_r_fx', 'walker_knee_r_on_tibia_r_in_tibia_r_fy', 'walker_knee_r_on_tibia_r_in_tibia_r_fz'],
            'Ankle': ['ankle_r_on_talus_r_in_talus_r_fx', 'ankle_r_on_talus_r_in_talus_r_fy', 'ankle_r_on_talus_r_in_talus_r_fz']}

EMG_muscle_mapping = {
    # Left Leg Muscles
    'Voltage_EMG1_vast_lat_l': ['vaslat_l', 'vasmed_l'],
    'Voltage_EMG3_rect_fem_l': ['recfem_l', 'sart_l', 'tfl_l'],
    'Voltage_EMG5_bic_fem_l': ['bflh_l', 'bfsh_l', 'semimem_l', 'semiten_l'],
    'Voltage_EMG7_glut_max_l': ['glmax1_l', 'glmax2_l', 'glmax3_l'],
    'Voltage_EMG9_gast_med_l': [],
    'Voltage_EMG13_add_mag_l': [],

    # Right Leg Muscles
    'Voltage_EMG2_vast_lat_r': ['vaslat_r', 'vasmed_r'],
    'Voltage_EMG4_rect_fem_r': ['recfem_r', 'sart_r', 'tfl_r'],
    'Voltage_EMG6_bic_fem_r': ['bflh_r', 'bfsh_r', 'semimem_r', 'semiten_r'],
    'Voltage_EMG8_glut_max_r': ['glmax1_r', 'glmax2_r', 'glmax3_r'],
    'Voltage_EMG10_gast_med_r': [],
    'Voltage_EMG14_add_mag_r': []
}

# session 2
EMG_muscle_mapping = {
    # Left Leg Muscles
    'EMG_Channels_EMG01_vast_lat_l': ['vaslat_l', 'vasmed_l'],
    'EMG_Channels_EMG03_rect_fem_l': ['recfem_l', 'sart_l', 'tfl_l'],
    'EMG_Channels_EMG05_bic_fem_l': ['bflh_l', 'bfsh_l', 'semimem_l', 'semiten_l'],
    'EMG_Channels_EMG07_glut_l': ['glmax1_l', 'glmax2_l', 'glmax3_l'],
    'EMG_Channels_EMG09_gast_med_l': [],

    # Right Leg Muscles
    'EMG_Channels_EMG02_vast_lat_r': ['vaslat_r', 'vasmed_r'],
    'EMG_Channels_EMG04_rect_fem_r': ['recfem_r', 'sart_r', 'tfl_r'],
    'EMG_Channels_EMG06_bic_fem_r': ['bflh_r', 'bfsh_r', 'semimem_r', 'semiten_r'],
    'EMG_Channels_EMG08_glut_r': ['glmax1_r', 'glmax2_r', 'glmax3_r'],
    'EMG_Channels_EMG10_gast_med_r': []
}

EMG_muscle_mapping = {
    'VM': ['vasmed_r'],
    'VL': ['vaslat_r'],
    'RF': ['recfem_r', 'sart_r', 'tfl_r'],
    'GRA': ['grac_r'],
    'ADDLONG': ['addlong_r', 'addbrev_r','addmagDist_r',
                'addmagIsch_r','addmagMid_r','addmagProx_r'],
    'SEMIMEM': ['semimem_r', 'semiten_r'],
    'BF': ['bflh_r', 'bfsh_r'],
    'GM': ['gasmed_r'],
    'GL': ['gaslat_r'],
    'MG': ['soleus_r'],
}

plot = {'Groups':
                    {'SO_StaticOptimization_force': Muscle_Groups,
                    'Analyse_SO_StaticOptimization_force_ReactionLoads': JCF_Groups,
                    'SO_StaticOptimization_force_normalised': Muscle_Groups,
                    'SO_StaticOptimization_activation': Muscle_Groups,
                    'MuscleForces_inputData': Muscle_Groups,
                    'inverse_dynamics': DOFs_moments},
                    
            'Summary': 
                    {'SO_StaticOptimization_force': 'Sum', 
                    'SO_StaticOptimization_force_normalised': 'mean',
                    'SO_StaticOptimization_activation': 'mean', 
                    'Analyse_SO_StaticOptimization_force_ReactionLoads': '3dsum',
                    'MuscleForces_inputData': 'Sum',
                    'inverse_dynamics': 'None' 
                    },
                    
                }

def _print():
    
    LOCAL_VARS = {k: v for k, v in globals().items() if not k.startswith('_')}
    print("Settings:")
    print(f"Subjects to analyse: {LOCAL_VARS['SUBJECTS_TO_ANALYSE']}")
    print(f"Trials to analyse: {LOCAL_VARS['TRIALS_TO_ANALYSE']}")
    print(f"DOFs: {LOCAL_VARS['DOFs']}")
    print(f"Muscle Groups:")
    for group, muscles in LOCAL_VARS['Muscle_Groups'].items():
        print(f"  {group}: {muscles}")
    print(f"JCF Groups:")
    for joint, components in LOCAL_VARS['JCF_Groups'].items():
        print(f"  {joint}: {components}")
    print(f"EMG Muscle Mapping:")
    for emg_channel, muscles in LOCAL_VARS['EMG_muscle_mapping'].items():
        print(f"  {emg_channel}: {muscles}")

def create_settings(trialPath=None):
        import xml.etree.ElementTree as ET
        import xml.dom.minidom
        
        if not trialPath:
            trialPath = input("Enter the trial path: ")
        
        settingsXMLPath = os.path.join(trialPath, 'trial_settings.xml')
        
        if os.path.exists(settingsXMLPath):
            print(f"Settings XML already exists at: {settingsXMLPath}")
            return
        
        # --- Add input template names
        settings = ET.Element('settings')
        inputs = Inputs(parentdir=trialPath)
        for varInput in inputs.__dict__.items():
            filepath = os.path.join(trialPath, varInput[1])
            
            if os.path.exists(filepath):
                ET.SubElement(settings, varInput[0]).text = os.path.relpath(filepath, trialPath)    
            else:
                ET.SubElement(settings, varInput[0]).text = varInput[1]
                
        # add CEINMS parameters
        ceinms_params = CEINMSParameters()
        ceinms_elem = ET.SubElement(settings, 'CEINMSParameters')
        for attr, value in ceinms_params.__dict__.items():
            if isinstance(value, list):
                list_elem = ET.SubElement(ceinms_elem, attr)
                for item in value:
                    if isinstance(item, dict):
                        item_elem = ET.SubElement(list_elem, 'ObjectiveFunction')
                        for k, v in item.items():
                            ET.SubElement(item_elem, k).text = str(v)
                    else:
                        ET.SubElement(list_elem, 'Item').text = str(item)
            else:
                ET.SubElement(ceinms_elem, attr).text = str(value)
        
        tree = ET.ElementTree(settings)
        rough_string = ET.tostring(tree.getroot(), 'utf-8')
        reparsed = xml.dom.minidom.parseString(rough_string)
        pretty_xml = reparsed.toprettyxml(indent="   ")
        # Remove blank lines
        pretty_xml_no_blanks = "\n".join([line for line in pretty_xml.splitlines() if line.strip()])
        with open(settingsXMLPath, 'w') as file:
            file.write(pretty_xml_no_blanks)

        print(f"Settings XML created at: {settingsXMLPath}")

        

if __name__ == "__main__":
    
    _print()
    create_settings()