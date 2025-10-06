import opensim as osim
import os

import pandas as pd
import numpy as np
import json

def muscle_arm_discontinuity(table_path, table_name, 
                             output_path, threshold = 0.005):
    df = pd.read_csv(os.path.join(table_path, table_name), index_col=0)
    time = list(df.index)
    muscles = list(df.columns)
    values = df.to_numpy()
    collection = {}
    for i, muscle in enumerate(muscles):
        dy = np.diff(values[:, i])
        discontinuity_ind = np.argwhere(dy > threshold)
        collection[muscle] = [time[j] for j in discontinuity_ind.flatten()] 
    # Serializing json
    json_object = json.dumps(collection, indent=4) 
    # Writing to json
    with open(f"{os.path.join(output_path, table_name[:-3])}_discontinuities.json", "w") as outfile:
        outfile.write(json_object)

def obtain_trc_times(trc_path):
    marker_data = osim.MarkerData(trc_path)
    recording_start, recording_stop = (marker_data.getStartFrameTime(), marker_data.getLastFrameTime())
    return recording_start, recording_stop

def obtain_mot_times(mot_path):
    table = osim.TimeSeriesTable(mot_path)
    time = table.getIndependentColumn()
    start, stop = time[0], time[-1]
    return start, stop

class MuscleMomentArms:
    def __init__ (self, kinematic_folder, kinematic_file, model_path, output_dir, time_start, time_end):

        
        self.kinematic_folder = kinematic_folder
        self.kinematic_file = kinematic_file
        self.model_path = model_path
        self.output_dir = output_dir
        self.time_start = time_start
        self.time_end = time_end
        self.model = osim.Model(model_path)
        self.motion = osim.Storage(os.path.join(self.kinematic_folder, self.kinematic_file))
        self.motion.lowpassIIR(6.)
        self.state = self.model.initSystem()
        self.numMuscles = self.model.getMuscles().getSize()
        self.time_vector()
    
    def time_vector(self):
        self.time = []
        self.frames = []        
        for i, t in enumerate(np.arange(0.0, self.motion.getLastTime(), 0.005)):
            if t >= self.time_start and t <= self.time_end:
                self.time.append(t)
                self.frames.append(i)

    def define_hip_cordinates(self):
        self.hip_flex_index_l = self.model.getCoordinateSet().getIndex('hip_flexion_l')
        self.hip_flex_coord_l = self.model.updCoordinateSet().get(self.hip_flex_index_l)
        self.hip_rot_index_l = self.model.getCoordinateSet().getIndex('hip_rotation_l')
        self.hip_rot_coord_l = self.model.updCoordinateSet().get(self.hip_rot_index_l)
        self.hip_add_index_l = self.model.getCoordinateSet().getIndex('hip_adduction_l')
        self.hip_add_coord_l = self.model.updCoordinateSet().get(self.hip_add_index_l)      
        self.hip_flex_index_r = self.model.getCoordinateSet().getIndex('hip_flexion_r')
        self.hip_flex_coord_r = self.model.updCoordinateSet().get(self.hip_flex_index_r)
        self.hip_rot_index_r = self.model.getCoordinateSet().getIndex('hip_rotation_r')
        self.hip_rot_coord_r = self.model.updCoordinateSet().get(self.hip_rot_index_r)
        self.hip_add_index_r = self.model.getCoordinateSet().getIndex('hip_adduction_r')
        self.hip_add_coord_r = self.model.updCoordinateSet().get(self.hip_add_index_r)

    def choose_hip_muscles(self):
        self.hip_muscle_indices = []; self.hip_muscle_names = []
        for i in range(self.numMuscles):
            str = self.model.getMuscles().get(i).getName()
            if 'add' in str or 'gl'in str  or 'semi'in str or 'bfl'in str or 'grac'in str or 'piri'in str or 'sart'in str or 'tfl'in str or 'iliac'in str or 'psoa'in str or 'rect'  in str:
                self.hip_muscle_indices.append(i)
                self.hip_muscle_names.append(str)
        #print('len_muscle_indices', len(self.hip_muscle_indices))
       
    def compute_hip_muscle_moment_arms(self, specific_muscles_list = None):
        self.define_hip_cordinates()
        self.choose_hip_muscles()

        # create empty moment arms vectors
        self.hip_flex_moment_arms = np.zeros((len(self.frames), len(self.hip_muscle_indices)))
        self.hip_add_moment_arms = np.zeros((len(self.frames), len(self.hip_muscle_indices)))
        self.hip_rot_moment_arms = np.zeros((len(self.frames), len(self.hip_muscle_indices)))

        for i, index in enumerate(self.frames):
            flexAngleL = self.motion.getStateVector(index).getData().get(self.hip_flex_index_l) / 180 * np.pi
            rotAngleL = self.motion.getStateVector(index).getData().get(self.hip_rot_index_l) / 180 * np.pi
            addAngleL = self.motion.getStateVector(index).getData().get(self.hip_add_index_l) / 180 * np.pi
            flexAngleR = self.motion.getStateVector(index).getData().get(self.hip_flex_index_r) / 180 * np.pi
            rotAngleR = self.motion.getStateVector(index).getData().get(self.hip_rot_index_r) / 180 * np.pi
            addAngleR = self.motion.getStateVector(index).getData().get(self.hip_add_index_r) / 180 * np.pi

            # Update the state with the joint angle
            coordSet = self.model.updCoordinateSet()
            coordSet.get(self.hip_flex_index_l).setValue(self.state, flexAngleL)
            coordSet.get(self.hip_rot_index_l).setValue(self.state, rotAngleL)
            coordSet.get(self.hip_add_index_l).setValue(self.state, addAngleL)
            coordSet.get(self.hip_flex_index_r).setValue(self.state, flexAngleR)
            coordSet.get(self.hip_rot_index_r).setValue(self.state, rotAngleR)
            coordSet.get(self.hip_add_index_r).setValue(self.state, addAngleR)

            # Realize the state to compute dependent quantities
            self.model.computeStateVariableDerivatives(self.state)
            self.model.realizeVelocity(self.state)

            # Compute the moment arm for each muscle
            for j in range(len(self.hip_muscle_indices)):
                muscleIndex = self.hip_muscle_indices[j]
                if self.hip_muscle_names[j][-1] == 'l':
                    flexMomentArm = self.model.getMuscles().get(muscleIndex).computeMomentArm(self.state, self.hip_flex_coord_l)
                    self.hip_flex_moment_arms[i,j] = flexMomentArm
                    rotMomentArm = self.model.getMuscles().get(muscleIndex).computeMomentArm(self.state, self.hip_rot_coord_l)
                    self.hip_rot_moment_arms[i,j] = rotMomentArm
                    addMomentArm = self.model.getMuscles().get(muscleIndex).computeMomentArm(self.state, self.hip_add_coord_l)
                    self.hip_add_moment_arms[i,j] = addMomentArm
                else:
                    flexMomentArm = self.model.getMuscles().get(muscleIndex).computeMomentArm(self.state, self.hip_flex_coord_r)
                    self.hip_flex_moment_arms[i,j] = flexMomentArm
                    rotMomentArm = self.model.getMuscles().get(muscleIndex).computeMomentArm(self.state, self.hip_rot_coord_r)
                    self.hip_rot_moment_arms[i,j] = rotMomentArm
                    addMomentArm = self.model.getMuscles().get(muscleIndex).computeMomentArm(self.state, self.hip_add_coord_r)
                    self.hip_add_moment_arms[i,j] = addMomentArm



        # record hip moment arms
        hip_flex_df = pd.DataFrame(self.hip_flex_moment_arms, index=self.time, columns=self.hip_muscle_names)
        hip_flex_df.to_csv(os.path.join(self.output_dir, 'hip_flex_muscle_moment_arms.csv'))
        
        hip_rot_df = pd.DataFrame(self.hip_rot_moment_arms, index=self.time, columns=self.hip_muscle_names)
        hip_rot_df.to_csv(os.path.join(self.output_dir, 'hip_rot_muscle_moment_arms.csv'))

        hip_add_df = pd.DataFrame(self.hip_add_moment_arms, index=self.time, columns=self.hip_muscle_names)
        hip_add_df.to_csv(os.path.join(self.output_dir, 'hip_add_muscle_moment_arms.csv'))

    def define_knee_cordinates(self):
        self.knee_flex_index_l = self.model.getCoordinateSet().getIndex('knee_angle_l')
        self.knee_flex_coord_l = self.model.updCoordinateSet().get(self.knee_flex_index_l)
        self.knee_flex_index_r = self.model.getCoordinateSet().getIndex('knee_angle_r')
        self.knee_flex_coord_r = self.model.updCoordinateSet().get(self.knee_flex_index_r)

    def choose_knee_muscles(self):
        self.knee_muscle_indices = []; self.knee_muscle_names = []
        #
        for i in range(self.numMuscles):
            str = self.model.getMuscles().get(i).getName()
            if 'bf' in str or 'gas'in str  or 'grac'in str or 'sart'in str or 'semi'in str or 'rec'in str or 'vas'in str :
                self.knee_muscle_indices.append(i)
                self.knee_muscle_names.append(str)

    def compute_knee_muscle_moment_arms(self):
        self.define_knee_cordinates()
        self.choose_knee_muscles()
        self.knee_state = self.model.initSystem()
        
        # create empty moment arms vectors
        self.knee_flex_moment_arms = np.zeros((len(self.frames), len(self.knee_muscle_indices)))

        # for each point in time            
        for i, index in enumerate(self.frames):
            # get joint angle for i
            flex_angle_l = self.motion.getStateVector(index).getData().get(self.knee_flex_index_l) / 180 * np.pi
            flex_angle_r = self.motion.getStateVector(index).getData().get(self.knee_flex_index_r) / 180 * np.pi
            
            # Update the state with the joint angle
            coordSet = self.model.updCoordinateSet()
            coordSet.get(self.knee_flex_index_l).setValue(self.knee_state, flex_angle_l)
            coordSet.get(self.knee_flex_index_r).setValue(self.knee_state, flex_angle_r)
            
            # Realize the state to compute dependent quantities
            self.model.computeStateVariableDerivatives(self.knee_state)
            self.model.realizeVelocity(self.knee_state)

            # Compute the moment arm for each muscle
            for j in range(len(self.knee_muscle_indices)):
                muscleIndex = self.knee_muscle_indices[j]
                if self.knee_muscle_names[j][-1] == 'l':
                    try:
                        flexMomentArm = self.model.getMuscles().get(muscleIndex).computeMomentArm(self.state, self.knee_flex_coord_l)
                        self.knee_flex_moment_arms[i,j] = flexMomentArm
                    except:
                        print('muscle', print(self.knee_muscle_names[j]), 'has no moment arm')
                else:
                  
                    try:
                        flexMomentArm = self.model.getMuscles().get(muscleIndex).computeMomentArm(self.state, self.knee_flex_coord_r)
                        self.knee_flex_moment_arms[i,j] = flexMomentArm
                    except:
                        print('muscle', print(self.knee_muscle_names[j]), 'has no moment arm')
        
        # record hip moment arms
        knee_flex_df = pd.DataFrame(self.knee_flex_moment_arms, index=self.time, columns=self.knee_muscle_names)
        knee_flex_df.to_csv(os.path.join(self.output_dir, 'knee_flex_muscle_moment_arms.csv'))
 
    def define_ankle_cordinates(self):
        self.ankle_flex_index_l = self.model.getCoordinateSet().getIndex('ankle_angle_l')
        self.ankle_flex_coord_l = self.model.updCoordinateSet().get(self.ankle_flex_index_l)
        self.ankle_flex_index_r = self.model.getCoordinateSet().getIndex('ankle_angle_r')
        self.ankle_flex_coord_r = self.model.updCoordinateSet().get(self.ankle_flex_index_r)

    def choose_ankle_muscles(self):
        self.ankle_muscle_indices = []; self.ankle_muscle_names = []
        for i in range(self.numMuscles):
            str = self.model.getMuscles().get(i).getName()
            if 'edl' in str or 'egl'in str  or 'gas'in str or 'per'in str or 'sol'in str or 'tib'in str:
                self.ankle_muscle_indices.append(i)
                self.ankle_muscle_names.append(str)

    def compute_ankle_muscle_moment_arms(self):
        self.define_ankle_cordinates()
        self.choose_ankle_muscles()

        # create empty moment arms vectors
        self.ankle_flex_moment_arms = np.zeros((len(self.frames), len(self.ankle_muscle_indices)))

        # for each point in time            
        for i, index in enumerate(self.frames):
            # get joint angle for i
            flex_angle_l = self.motion.getStateVector(index).getData().get(self.ankle_flex_index_l) / 180 * np.pi
            flex_angle_r = self.motion.getStateVector(index).getData().get(self.ankle_flex_index_r) / 180 * np.pi
       
            # Update the state with the joint angle
            coordSet = self.model.updCoordinateSet()
            coordSet.get(self.ankle_flex_index_l).setValue(self.state, flex_angle_l)
            coordSet.get(self.ankle_flex_index_r).setValue(self.state, flex_angle_r)
            
            # Realize the state to compute dependent quantities
            self.model.computeStateVariableDerivatives(self.state)
            self.model.realizeVelocity(self.state)

            # Compute the moment arm for each muscle
            for j in range(len(self.ankle_muscle_indices)):
                muscle_index = self.ankle_muscle_indices[j]
                if self.ankle_muscle_names[j][-1] == 'l':
                    flex_moment_arm = self.model.getMuscles().get(muscle_index).computeMomentArm(self.state, self.ankle_flex_coord_l)
                    self.ankle_flex_moment_arms[i,j] = flex_moment_arm
                else:
                    flex_moment_arm = self.model.getMuscles().get(muscle_index).computeMomentArm(self.state, self.ankle_flex_coord_r)
                    self.ankle_flex_moment_arms[i,j] = flex_moment_arm
        
        # record hip moment arms
        ankle_flex_df = pd.DataFrame(self.ankle_flex_moment_arms, index=self.time, columns=self.ankle_muscle_names)
        ankle_flex_df.to_csv(os.path.join(self.output_dir, 'ankle_flex_muscle_moment_arms.csv'))


    def find_problem_muscles(self, min_discontinuity=0.004):  

        def check_discontinuity(ma_to_check, muscles_to_check):
            # ma_to_check is a t*m np.array, muscles_to_check is a list
            temp = []
            for i, muscle in enumerate(muscles_to_check):
                dy = np.diff(ma_to_check[:, i])
                discontinuity_ind = np.argwhere(dy > min_discontinuity)
                if len(discontinuity_ind) > 0:
                    temp.append(muscle)
            return temp
        
        problem_muscles = []
        try: 
            ma_to_check = self.hip_rot_moment_arms
            muscles_to_check = self.hip_muscle_names
            problem_muscles = problem_muscles + check_discontinuity(ma_to_check, muscles_to_check)
        except: print('no hip flex  moments to check')

        try: 
            ma_to_check = self.hip_rot_moment_arms
            muscles_to_check = self.hip_muscle_names
            problem_muscles = problem_muscles + check_discontinuity(ma_to_check, muscles_to_check)
        except: print('no hip rot moments to check') 
        
        try: 
            ma_to_check = self.hip_add_moment_arms
            muscles_to_check = self.hip_muscle_names
            problem_muscles = problem_muscles + check_discontinuity(ma_to_check, muscles_to_check)
        except: print('no hip add moments to check')

        try: 
            ma_to_check = self.knee_flex_moment_arms
            muscles_to_check = self.knee_muscle_names
            problem_muscles = problem_muscles + check_discontinuity(ma_to_check, muscles_to_check)
        except: print('no knee moments to check') 

        try: 
            ma_to_check = self.ankle_flex_moment_arms
            muscles_to_check = self.ankle_muscle_names
            problem_muscles = problem_muscles + check_discontinuity(ma_to_check, muscles_to_check)
        except: print('no ankle moments to check') 

        self.problem_muscles_set = list(set(problem_muscles))
        self.moment_arms_are_wrong = False
        if len(self.problem_muscles_set) > 0:
           self.moment_arms_are_wrong = True
        return self.problem_muscles_set, self.moment_arms_are_wrong
            
    def reduce_wraps_iteratively(self, max_iterations=10, step_size=0.001):
        # use with one trial only
            
            if len(self.problem_muscles_set) > 0:
                new_model_path = self.model_path.replace('.osim', '_modWO.osim')
                import shutil
                shutil.copy(self.model_path, new_model_path)

                path_to_new_ma = os.path.join(self.output_dir, 'muscle_moment_arms', 'improve_wo')
                if not os.path.exists(path_to_new_ma):
                    os.makedirs(path_to_new_ma)

                # Check and adjust muscle moment arms
                failed = False
                iteration = 0
                wrap_objects_modified = []
                wrap_objects_orig_radius = []
                wrap_objects_modified_radius = []
                muscles_with_discontinuities = self.problem_muscles_set
                
                moment_arms_are_wrong = self.moment_arms_are_wrong
                while moment_arms_are_wrong and iteration < max_iterations:
                    if iteration != 1:
                        print(f'Closing previous figures for iteration {iteration}')
                    
                    iteration += 1
                    model = osim.Model(new_model_path)
                    model.initSystem()

                    if muscles_with_discontinuities:
                        made_modifications = False
                        
                        for muscle_name in muscles_with_discontinuities:
                            print(f'Processing muscle {muscle_name}')
                            muscle = model.getMuscles().get(muscle_name)
                            geo_path = muscle.getGeometryPath()
                            wrap_set = geo_path.getWrapSet()
                            
                            for w in range(wrap_set.getSize()):
                                wrap_obj = wrap_set.get(w)
                                wrap_obj_name = wrap_obj.getWrapObjectName()

                                for body in model.getBodySet():
                                    for j in range(body.getWrapObjectSet().getSize()):
                                        wrap_object = body.getWrapObjectSet().get(j)

                                        if wrap_object.getName() == wrap_obj_name:
                                            try:
                                                wrap_cylinder = osim.WrapCylinder.safeDownCast(wrap_object)
                                                radius = wrap_cylinder.get_radius()
                                                if radius - step_size > 0:
                                                    wrap_cylinder.set_radius(radius - step_size)
                                                    print(f'{wrap_obj_name}: radius decreased to {radius - step_size}')
                                                    model.printToXML(new_model_path)
                                                    print(f'model saved')
                                                    
                                                    wrap_objects_modified.append(wrap_obj_name)
                                                    wrap_objects_orig_radius.append(radius)
                                                    wrap_objects_modified_radius.append(radius - step_size)
                                                    made_modifications = True
                                                    break
                                                else:
                                                    print(f'{muscle_name} moment arm error; wrap object is already too small. Manual check needed.')
                                                    failed = True
                                                    moment_arms_are_wrong = False
                                            except Exception:
                                                pass
                        # Check updated model for moment arm discontinuities
                        if made_modifications:
                            ma_calculator = MuscleMomentArms(self.kinematic_folder, self.kinematic_file, new_model_path, path_to_new_ma, self.time_start, self.time_end)
                            ma_calculator.compute_hip_muscle_moment_arms()
                            ma_calculator.compute_knee_muscle_moment_arms()
                            ma_calculator.compute_ankle_muscle_moment_arms()
                            muscles_with_discontinuities, moment_arms_are_wrong = ma_calculator.find_problem_muscles()
                            print(f'muscles with errors are {muscles_with_discontinuities}')
                        else:
                            print('Some moment arms could not be adjusted automatically. Manual check recommended.')
                            moment_arms_are_wrong = False
                            failed = True
                    else:
                        moment_arms_are_wrong = False

                if not failed:
                    unique_wrap_objects = list(set(wrap_objects_modified))
                    print('SUMMARY:')
                    for obj in unique_wrap_objects:
                        indices = [i for i, x in enumerate(wrap_objects_modified) if x == obj]
                        print(f'{obj} radius reduced from {wrap_objects_orig_radius[indices[0]]} to {wrap_objects_modified_radius[indices[-1]]}')
                    print(f'Modified model saved as {new_model_path}')
                else:
                    print('Process failed after reaching maximum iterations.')










