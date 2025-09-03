import os
import time
from matplotlib import pyplot as plt
import numpy as np
import opensim as osim

import pandas as pd

try:
    import utils
    import paths
except ImportError:
    from . import utils
    from . import paths


def coordinates_per_muscle(osimModel, muscle_name):
    coords = []
    muscle = osimModel.getMuscles().get(muscle_name)
    coord_set = osimModel.getCoordinateSet()
    state = osimModel.initSystem()
    osimModel.realizePosition(state)
    
    for i in range(coord_set.getSize()):
        coord = coord_set.get(i)
        if abs(muscle.computeMomentArm(state, coord)) > 1e-4:
            coords.append(coord.getName())
            
    return coords

def muscles_per_coordinate(osimModel, coord_name):
    muscles = []
    coord = osimModel.getCoordinateSet().get(coord_name)
    state = osimModel.initSystem()
    osimModel.realizePosition(state)

    for i in range(osimModel.getMuscles().getSize()):
        muscle = osimModel.getMuscles().get(i)
        if abs(muscle.computeMomentArm(state, coord)) > 1e-4:
            muscles.append(muscle.getName())

    return muscles


def checkMuscleMomentArms(osim_modelPath, ik_output,  coordinate_list, threshold = 0.005):

    def get_model_coord(model, coord_name):
        try:
            index = model.getCoordinateSet().getIndex(coord_name)
            coord = model.updCoordinateSet().get(index)
        except:
            index = None
            coord = None
            print(f'Coordinate {coord_name} not found in model')
        
        return index, coord

    def muscle_crosses_coordinate(osimModel, muscle_name, coord_name):
        
        coord_list = coordinates_per_muscle(osimModel, muscle_name)
        if coord_name in coord_list:
            return True
        
        return False

    def set_model_state(model, motion,state, frame):

        # coordinate set
        coordSet = model.getCoordinateSet()
        pose = {}
        for coord in coordSet:
            index = coordSet.getIndex(coord)
            angle = motion.getStateVector(frame).getData().get(index) / 180 * np.pi
            coordSet = model.updCoordinateSet()
            coordSet.get(index).setValue(state, angle)
            pose[coord.getName()] = angle
        
        # Realize the state to compute dependent quantities
        model.computeStateVariableDerivatives(state)
        model.realizeVelocity(state)

        return state, model, coordSet, pose
    
    # Load motions and model
    motion = osim.Storage(ik_output)
    model = osim.Model(osim_modelPath)

    # Initialize system and state
    model.initSystem()
    state = model.initSystem()
    coordSet = model.getCoordinateSet()

    for i in range(coordSet.getSize()):
    
        coordinate = coordSet.get(i)
        if coordinate.getName() not in coordinate_list:
            continue    
        
        print(f'Processing coordinate: {coordinate.getName()}\n\n')
        time.sleep(1)
        
        # get names of muscles
        Index, Coord = get_model_coord(model, coordinate)
        muscle_names = muscles_per_coordinate(osimModel, Coord.getName())
        # compute moment arms for each muscle and create time vector
        time_vector = []
        moment_arms = {}    
        initial_time = time.time()
        
        for i in range(1, motion.getSize()):
            state, model, coordSet, pose = set_model_state(model, motion, state, i-1)
            
            time_vector.append(motion.getStateVector(i-1).getTime())
            
            for j, muscle_name in enumerate(muscle_names):
                moment_arm = model.getMuscles().get(muscle_name).computeMomentArm(state, coordSet.get(Index))
                moment_arms[muscle_name] = moment_arms.get(muscle_name, []) + [moment_arm]

            # print every 50th frame
            if i % 50 == 0:
                frame_time = time.time() - initial_time
                print(f'frame {i} took {frame_time:.6f} seconds')
                initial_time = time.time()

        # make a dataframe
        df = pd.DataFrame(moment_arms, index=time_vector)
        df.index.name = 'time'
        df.columns.name = 'Muscles'
        
        utils.write_sto_file(df, os.path.join(os.path.dirname(ik_output),'moment_arms' ,f'{coordinate.getName()}.sto'))


base_dir = paths.SIMULATION_DIR
subject = 'Athlete_03'  # Replace with actual subject name
session = '22_07_06'  # Replace with actual session name
trial = 'sq_70'  # Replace with actual trial name

# create a trial instance
trial = paths.Trial(subject_name=subject, session_name=session, trial_name=trial)

osimModel = osim.Model(trial.USED_MODEL)
muscles = osimModel.getMuscles()
joint_angles = osim.Storage(trial.outputFiles['IK'].abspath())

muscles = muscles_per_coordinate(osimModel, coord_name='hip_flexion_l')

coordinates_to_check = ['hip_flexion_l', 'hip_flexion_r']

checkMuscleMomentArms(osim_modelPath=osimModel,
                      ik_output=trial.outputFiles['IK'].abspath(),
                      threshold=0.005, 
                      coordinate_list=coordinates_to_check)
