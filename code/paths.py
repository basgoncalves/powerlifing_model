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

CODE, _ = utils.check_path(os.path.dirname(__file__))
POWERLIFTING_DIR, _ = utils.check_path(os.path.dirname(CODE), isdir=True)
MODELS_DIR, _ = utils.check_path(os.path.join(POWERLIFTING_DIR, 'models'), isdir=True)
SETUP_DIR, _ = utils.check_path(os.path.join(POWERLIFTING_DIR, 'SetupFiles\Purzel'), isdir=True)
SIMULATION_DIR, _ = utils.check_path(os.path.join(POWERLIFTING_DIR, 'simulations'), isdir=True)
RESULTS_DIR, _ = utils.check_path(os.path.join(POWERLIFTING_DIR, 'results'), isdir=True)

class Settings():
    def __init__(self):
        self.TRIAL_TO_ANALYSE = ['dl_75','sq_70','sq_80','sq_90']
        
        self.DOFs = ['hip_flexion_l', 'hip_flexion_r',
                     'hip_adduction_l', 'hip_adduction_r',
                     'hip_rotation_l', 'hip_rotation_r',
                     'knee_angle_l', 'knee_angle_r',
                     'ankle_angle_l', 'ankle_angle_r']
        
        self.Muscle_Groups = { 'Adductors': ['addbrev_r','addlong_r','addmagDist_r','addmagIsch_r','addmagMid_r','addmagProx_r','grac_r'],
            'Hamstrings': ['bflh_r','semimem_r','semiten_r','bfsh_r'],
            'Gluteus maximus':['glmax1_r','glmax2_r','glmax3_r'],
            'Gluteus medius':['glmed1_r','glmed2_r','glmed3_r'],
            'Gluteus minimus':['glmin1_r','glmin2_r','glmin3_r'],
            'Hip flexors':['sart_r','recfem_r','tfl_r','iliacus_r','psoas_r'],            
            'Triceps Surae':['soleus_r','gaslat_r','gasmed_r'],
            'Vasti':['vasint_r','vaslat_r','vasmed_r']
            }

        self.JCF_Groups = {'Hip': ['hip_r_on_femur_r_in_femur_r_fx', 'hip_r_on_femur_r_in_femur_r_fy', 'hip_r_on_femur_r_in_femur_r_fz'],
                    'Knee': ['walker_knee_r_on_tibia_r_in_tibia_r_fx', 'walker_knee_r_on_tibia_r_in_tibia_r_fy', 'walker_knee_r_on_tibia_r_in_tibia_r_fz'],
                    'Ankle': ['ankle_r_on_talus_r_in_talus_r_fx', 'ankle_r_on_talus_r_in_talus_r_fy', 'ankle_r_on_talus_r_in_talus_r_fz']}

        self.EMG_muscle_mapping = {
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

        self.plot = {'Groups':
                            {'SO_StaticOptimization_force': self.Muscle_Groups,
                            'Analyse_JRA_ReactionLoads': self.JCF_Groups,
                            'SO_StaticOptimization_force_normalised': self.Muscle_Groups,
                            'SO_StaticOptimization_activation': self.EMG_muscle_mapping},
                    'Summary': 
                            {'SO_StaticOptimization_force': 'Sum', 
                             'SO_StaticOptimization_force_normalised': 'mean',
                            'SO_StaticOptimization_activation': 'mean', 
                            'Analyse_JRA_ReactionLoads': '3dsum'}
                        }

class Session():
    def __init__(self, subject_name, session_name):
        self.subject = subject_name
        self.name = session_name
        self.path = os.path.join(SIMULATION_DIR, self.subject, self.name)
        
        if not os.path.exists(self.path):
            print(f"Session path does not exist: {self.path}")
        
        self.TRIALS = [trial for trial in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, trial))]
        
        # only keep trials that are in the settings
        settings = Settings()
        self.TRIALS = [Trial(self.subject, self.name, trial) for trial in self.TRIALS if trial in settings.TRIAL_TO_ANALYSE]

class Subject():
    def __init__(self, subject_name):
        self.name = subject_name
        self.path = os.path.join(SIMULATION_DIR, self.name)
        
        if not os.path.exists(self.path):
            print(f"Subject path does not exist: {self.path}")
        
        self.SESSIONS = [Session(self.name, session) for session in os.listdir(self.path) if os.path.isdir(os.path.join(self.path, session))]
        
        # sort sessions by date
        self.SESSIONS.sort(key=lambda x: x.name)
        
class Analysis():
    def __init__(self):
        self.subject_list = [subject for subject in os.listdir(SIMULATION_DIR) if os.path.isdir(os.path.join(SIMULATION_DIR, subject))]
        self.SUBJECTS = [Subject(subject) for subject in self.subject_list]   
        self.SUBJECTS.sort(key=lambda x: x.name)  
        
    def get_subject(self, subject_name):
        """
        Returns the Subject object by name or index.
        If subject_name is int, returns the subject at that index.
        """
        if isinstance(subject_name, int):
            if 0 <= subject_name < len(self.SUBJECTS):
                return self.SUBJECTS[subject_name]
            else:
                print("Subject index out of range.")
                return None
        else:
            for subj in self.SUBJECTS:
                if subj.name == subject_name:
                    return subj
            
class Models(Analysis):
    def __init__(self, subject_name='Athlete_03'):
                
        self.SCALED_MODEL = os.path.join(MODELS_DIR, f'{subject_name}_linearly_scaled.osim')        
        self.MRI_MODEL = os.path.join(MODELS_DIR, f'{subject_name}_mri_scaled.osim')
        
        self.SCALED_MODEL_SCALED_MASSES = os.path.join(MODELS_DIR, self.SCALED_MODEL.replace('.osim', '_scaledMasses.osim'))
        self.MRI_MODEL_SCALED_MASSES = os.path.join(MODELS_DIR, self.MRI_MODEL.replace('.osim', '_scaledMasses.osim'))
        
        self.SCALED_MODEL_INCREASED_FORCE = os.path.join(MODELS_DIR, f'{subject_name}_linearly_scaled_increased_20.00.osim')
        self.MRI_MODEL_INCREASED_FORCE = os.path.join(MODELS_DIR, f'{subject_name}_mri_scaled_increased_20.00.osim')
        
        self.CATELI_MODEL = os.path.join(MODELS_DIR, f'{subject_name}_Catelli_final.osim')
        
class Step():
    def __init__(self, function=None, setup=None, output=None, parentdir=None):
        self.function = function
        self.setup = setup
        self.output = output
        self.parentdir = parentdir
        
    def abspath(self):
        return os.path.join(self.parentdir, self.output)

class Trial():
    def __init__(self, subject_name, session_name, trial_name):
        
        self.subject = subject_name
        self.session = session_name
        self.name = trial_name
        self.path = os.path.join(SIMULATION_DIR, self.subject, self.session, self.name)
        
        models = Models(subject_name)
        
        if subject_name.lower().__contains__('mri'):  # Edit model paths below
            self.USED_MODEL = models.MRI_MODEL_SCALED_MASSES
        else:
            self.USED_MODEL = models.SCALED_MODEL_SCALED_MASSES
        
        self.inputFiles = {
            'C3D': Step(function=None, setup=None, output='c3dfile.c3d', parentdir=self.path),
            'MARKERS': Step(function=None, setup=None, output='marker_experimental.trc', parentdir=self.path),
            'EMG_MOT': Step(function=None, setup=None, output='EMG_filtered.sto', parentdir=self.path),
            'EMG_MOT_NORMALISED': Step(function=None, setup=None, output='EMG_filtered_normalised.sto', parentdir=self.path),
            'GRF_MOT': Step(function=None, setup=None, output='grf.mot', parentdir=self.path),
            'GRF_XML': Step(function=None, setup=None, output='externalloads.xml', parentdir=self.path),
            'EVENTS': Step(function=None, setup=None, output='events.csv', parentdir=self.path),
            'ACTUATORS_SO': Step(function=None, setup=None, output='actuators_so.xml', parentdir=self.path),
            'CALIBRATION_CFG': Step(function=None, setup=None, output='../calibrationCfg_ceinms-nn_hybrid.xml', parentdir=self.path),
            'CEINMS_EXCITATION_GENERATOR': Step(function=None, setup=None, output='../excitationGenerator.xml', parentdir=self.path),
            'CEINMS_INPUT_DATA': Step(function=None, setup=None, output='inputData.xml', parentdir=self.path),
            'CEINMS_RUN_OPTIMISE_BAT': Step(function=None, setup=None, output='run_ceinms_nn_optimise.bat', parentdir=self.path),
        }

        self.outputFiles = {
            'IK': Step(function='run_ik.main', setup='setup_IK.xml', output='joint_angles.mot', parentdir=self.path),
            'ID': Step(function='run_id.main', setup='setup_ID.xml', output='inverse_dynamics.sto', parentdir=self.path),
            'MA': Step(function='run_ma.main', setup='setup_MA.xml', output='muscleAnalysis', parentdir=self.path),
            'SO': Step(function='run_so.main', setup='setup_SO.xml', output='', parentdir=self.path),
            'JRA': Step(function='run_jra.main', setup='setup_JRA.xml', output='Analyse_JRA_ReactionLoads.sto', parentdir=self.path),
            'CEINMS_CALIBRATION': Step(function='run_ceinms_calibration.main', 
                                       setup='../calibrationSetup_ceinms-nn_hybrid.xml', 
                                       output='../ceinms_calibration_results',
                                       parentdir=self.path),
            
            'CEINMS_OPTIMISE': Step(function='run_ceinms_optimise.main',
                                        setup='optimiseSetup_ceinms-nn_hybrid.xml', 
                                        output='ceinms_optimise_results',
                                        parentdir=self.path),
        }
        
        try:
            events_path = os.path.join(self.path, self.inputFiles['EVENTS'].output)
            events = pd.read_csv(events_path, index_col=0, header=None)
            self.TIME_RANGE = [events.iloc[0, 0], events.iloc[1, 0]]
            if any(pd.isna(self.TIME_RANGE)):
                print(f"Warning: Time range in {self.inputFiles['EVENTS']} is not set.")
                self.TIME_RANGE = None
        except Exception as e:
            print(f"Warning: Events file {self.inputFiles['EVENTS'].output} not found.")
            self.TIME_RANGE = None
        
    def copy_inputs_to_trial(self, replace=False):
        
        # copy input files from SETUP_DIR to trial directory
        for key, step in self.inputFiles.items():
            if step.output:
                source = os.path.join(SETUP_DIR, step.output)
                target = os.path.join(self.path, step.output)
                
                # check if target exists and replace if needed
                if not os.path.exists(target) or replace:
                    if os.path.exists(source):
                        # create target directory if it does not exist
                        shutil.copy(source, target)
                        print(f"Copied {source} to {target}")
                        
                    else:
                        print(f"Source file does not exist: {source}")
                        
                else:
                    print(f"Target file already exists: {target}")
        
    def print_settings(self):
        """Print the paths for debugging."""
        print("CODE:", CODE)
        print("POWERLIFTING_DIR:", POWERLIFTING_DIR)
        
        print(f"Subject: {self.subject}")
        print(f"Session: {self.session}")
        print(f"Trial: {self.name}")
        print(f"Trial path: {self.path}")
        
        print(f"Used model: {self.USED_MODEL}")
        
        time.sleep(1)  # Optional: wait for a second before printing
      
    def fullpath(self, filename):
        return os.path.join(self.path, filename)
    
    
if __name__ == "__main__":
    
    settings = Settings()
    analysis = Analysis()
    trial = Trial(subject_name = analysis.SUBJECTS[0].name,
                session_name = analysis.SUBJECTS[0].SESSIONS[0].name,
                trial_name = settings.TRIAL_TO_ANALYSE[0])

    trial.copy_inputs_to_trial(replace=False)

    trial.print_settings()


# END