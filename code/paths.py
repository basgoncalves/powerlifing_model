import os
import shutil
import time
import pandas as pd
import utils
import opensim as osim

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
SETUP_DIR, _ = utils.check_path(os.path.join(CODE, 'SetupFiles\Purzel'), isdir=True)

POWERLIFTING_DIR, _ = utils.check_path(os.path.dirname(CODE), isdir=True)
MODELS_DIR, _ = utils.check_path(os.path.join(POWERLIFTING_DIR, 'models'), isdir=True)

SIMULATION_DIR, _ = utils.check_path(os.path.join(POWERLIFTING_DIR, 'simulations'), isdir=True)
RESULTS_DIR, _ = utils.check_path(os.path.join(POWERLIFTING_DIR, 'results'), isdir=True)

class Settings():
    def __init__(self):
        self.TRIAL_TO_ANALYSE = ['sq_70','sq_75','sq_80','sq_85','sq_90']
        
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
                            'SO_StaticOptimization_activation': self.Muscle_Groups},
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
    """Class to manage analysis of subjects and their trials.
    
    Usage:
    analysis = Analysis()
    subject = analysis.get_subject('Athlete_03')  # Get subject by name
    subject = analysis.get_subject(0)  # Get subject by index"""
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
        
        self.SCALED_MODEL_INCREASED_FORCE = os.path.join(MODELS_DIR, f'{subject_name}_linearly_scaled_scaledMasses_increased_3.00.osim')
        self.MRI_MODEL_INCREASED_FORCE = os.path.join(MODELS_DIR, f'{subject_name}_scaled_scaledMasses_increased_20.00.osim')
        
        self.CATELI_MODEL = os.path.join(MODELS_DIR, f'{subject_name}_Catelli_final.osim')
    
class Step():
    def __init__(self, function=None, setup=None, output=None, parentdir=None):
        self.function = function
        self.setup = setup
        self.output = output
        self.parentdir = parentdir
        
    def abspath(self):
        return os.path.join(self.parentdir, self.output)
    
    def path(self):
        return os.path.join(self.parentdir, self.output) if self.parentdir else self.output

class Trial():
    def __init__(self, subject_name, session_name, trial_name):
        
        self.subject = subject_name
        self.session = session_name
        self.name = trial_name
        self.path = os.path.join(SIMULATION_DIR, self.subject, self.session, self.name)
        
        models = Models(subject_name)
        
        # Edit model paths below
        if subject_name.lower().__contains__('mri'):  
            self.USED_MODEL = models.MRI_MODEL_INCREASED_FORCE
        else:
            self.USED_MODEL = models.SCALED_MODEL_INCREASED_FORCE
        
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
            'FORCES_SO': Step(function=None, setup=None, output='SO_StaticOptimization_force.sto', parentdir=self.path),
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

    def copy_inputs_to_trial(self, replace: bool = False):

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
        
        # copy setups from the outputFiles to the trial directory
        for key, step in self.outputFiles.items():
            if step.setup:
                source = os.path.join(SETUP_DIR, step.setup)
                target = os.path.join(self.path, step.setup)
                
                # check if target exists and replace if needed
                if not os.path.exists(target) or replace:
                    if os.path.exists(source):
                        # create target directory if it does not exist
                        shutil.copy(source, target)
                        print(f"Copied {source} to {target}")
                        
                    else:
                        print(f"Source setup file does not exist: {source}")
                        
                else:
                    print(f"Target setup file already exists: {target}")
    
    def check_paths(self):
        """Loop through all subjects sessions and trials and run_ik 
        for each trial. or print error to log if could not run."""
        for subject in self.subjects:
            for session in subject.sessions:
                for trial in session.trials:
                    try:
                        self.run_ik(trial)
                    except Exception as e:
                        utils.print_to_log(f"Error running IK for {trial}: {e}")

    def validate_markers_used(ikTool: osim.InverseKinematicsTool, markers_path: str):
        task_set = ikTool.get_IKTaskSet()
        markers = utils.load_trc(markers_path)
        
        markers_list = [col for col in markers.columns if col.strip()]
        
        for task in task_set:
            if task.getName() in markers_list:
                task.setApply(True)
                task.setWeight(1.0)
            else:
                task.setApply(False)
            print(f"Task: {task.getName()}, Apply: {task.getApply()}, Weight: {task.getWeight()}")
        
        return ikTool

    def run_ik(self, osim_modelPath: str = None,
               marker_trc: str = None,
               ik_output: str = None,
               setup_xml: str = None,
               time_range: tuple = None,
               resultsDir: str = None):
        
        if osim_modelPath is None:
            osim_modelPath = self.USED_MODEL 
            
        if marker_trc is None:
            marker_trc = self.inputFiles['MARKERS'].path()
            
        if ik_output is None:
            ik_output = self.outputFiles['IK'].abspath()
            
        if setup_xml is None:
            setup_xml = self.outputFiles['IK'].path()
            
        if resultsDir is None:
            resultsDir = self.path
            
        os.chdir(resultsDir)
        if not os.path.exists(resultsDir):
            os.makedirs(resultsDir)

        if not os.path.exists(osim_modelPath):
            utils.print_to_log(f"OpenSim model file not found: {osim_modelPath}")
        
        if not os.path.exists(marker_trc):
            utils.print_to_log(f"Marker TRC file not found: {marker_trc}")

        # Load the model
        print(f"Loading OpenSim model from {osim_modelPath}")
        model = osim.Model(osim_modelPath)
        model.initSystem()

        # Create the Inverse Kinematics tool
        ikTool = osim.InverseKinematicsTool(setup_xml)
        
        # simple function to validate the markers used in the IK setup
        ikTool = self.validate_markers_used(ikTool, marker_trc)
        
        # Set the model and parameters
        ikTool.setModel(model)
        # Set the marker data file and time range
        ikTool.setMarkerDataFileName(marker_trc)
        
        # set the time range for the IK calculation
        if time_range is not None:
            ikTool.setStartTime(time_range[0])  # Set start time
            ikTool.setEndTime(time_range[1])    # Set end time
        
        # Set the output motion file name relative to the results directory
        ikTool.setResultsDir('./')
        ikTool.setOutputMotionFileName(ik_output)
        ikTool.printToXML(setup_xml)
        print(f"Inverse Kinematics setup saved to {setup_xml}")
        time.sleep(1)  # Optional: wait for a second before running the tool
        
        # Reload tool from xml
        ikTool = osim.InverseKinematicsTool(setup_xml)
        ikTool.setModel(model)
        
        # Run the inverse kinematics calculation
        ikTool.run()
        
        print(f"Inverse Kinematics calculation completed. Results saved to {resultsDir}")


        
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