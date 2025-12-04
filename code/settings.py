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
    
class Execute:
    ''' Logics for which analyses to execute '''
    def __init__(self):
        
        self.replace = False

        self.INCREASE_MUSCLE_FORCE = False
        self.SCALE_FACTOR = 3
        self.exportC3D = False
        self.IK = True
        self.ID = True
        self.MA = True
        self.MOMENT_ARMS = True
        self.SO = True
        self.JRA = True
        
        self.EMG_NORMALISE = True
        self.SCALE_EMG = False
        self.EMG_SCALE_FACTOR = 0.7
        
        self.CREATE_CEINMS_FILES = True
        self.CREATE_CEINMS_MODEL = False
        
        self.CEINMS_CALIBRATION = False
        self.CEINMS_CALIBRATION_PLOTS = False
        
        self.CEINMS_OPTIMISATION = False
        self.CEINMS_EXE = True
        self.CEINMS_EXE_LOOP = False
        
        self.JRA_CEINMS = False
        
        self.CREATE_PLOTS = False
        
        self.PLOT_IK = True
        self.PLOT_ID = True
        self.PLOT_MA = True
        self.PLOT_SO = True
        self.PLOT_JRA = True
        self.PLOT_EMG = True
        
        
        self.push_to_git = True
               
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
# Muscle_Groups = {'R Gluteus maximus':['glmax1_r','glmax2_r','glmax3_r'],
#                         'R Gluteus medius':['glmed1_r','glmed2_r','glmed3_r'],
#                         'R Gluteus minimus':['glmin1_r','glmin2_r','glmin3_r'], 
#                         'R Adductor Magnus': ['addmagDist_r','addmagIsch_r','addmagMid_r','addmagProx_r'],
#                         'R Biceps Femoris': ['bflh_r','bfsh_r'],
#                         'R Semimembranosus': ['semimem_r'],
#                         'R Semitendinosus': ['semiten_r'],
#                         'R Rectus Femoris': ['recfem_r'],
#                         'R Vasti':['vasint_r','vaslat_r','vasmed_r'],
#                         'R Gastrocnemius': ['gaslat_r','gasmed_r'],
#                         'R Soleus': ['soleus_r'],
#                         'L Gluteus maximus':['glmax1_l','glmax2_l','glmax3_l'],
#                         'L Gluteus medius':['glmed1_l','glmed2_l','glmed3_l'],
#                         'L Gluteus minimus':['glmin1_l','glmin2_l','glmin3_l'],
#                         'L Adductor Magnus': ['addmagDist_l','addmagIsch_l','addmagMid_l','addmagProx_l'],
#                         'L Biceps Femoris': ['bflh_l','bfsh_l'],
#                         'L Semimembranosus': ['semimem_l'],
#                         'L Semitendinosus': ['semiten_l'],
#                         'L Rectus Femoris': ['recfem_l'],
#                         'L Vasti':['vasint_l','vaslat_l','vasmed_l'],
#                         'L Gastrocnemius': ['gaslat_l','gasmed_l'],
#                         'L Soleus': ['soleus_l']}

Muscle_Groups = {'R Gluteus maximus':['glmax1_r','glmax2_r','glmax3_r'],
                        'R Gluteus medius':['glmed1_r','glmed2_r','glmed3_r'],
                        'R Gluteus minimus':['glmin1_r','glmin2_r','glmin3_r'], 
                        'R Adductor Magnus': ['addmagDist_r','addmagIsch_r','addmagMid_r','addmagProx_r'],
                        'R Biceps Femoris': ['bflh_r','bfsh_r'],
                        'R Semimembranosus': ['semimem_r'],
                        'R Semitendinosus': ['semiten_r'],
                        'R Rectus Femoris': ['recfem_r'],
                        'R Vasti':['vasint_r','vaslat_r','vasmed_r'],
                        'R Triceps Surae': ['soleus_r','gaslat_r','gasmed_r']
                        }

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

# running session
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
