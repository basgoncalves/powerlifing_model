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

def checkMuscleMomentArms(osim_modelPath, ik_output, leg = 'l', threshold = 0.005):

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
        state = model.initSystem()
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

    coordinate = 'hip_flexion_' + leg
    
    # get names of muscles
    Index, Coord = get_model_coord(model, coordinate)
    muscle_names = muscles_per_coordinate(osimModel, Coord.getName())
    # compute moment arms for each muscle and create time vector
    time_vector = []
    moment_arms = {}    
    for i in range(1, motion.getSize()):
        initial_time = time.time()
        state, model, coordSet, pose = set_model_state(model, motion, state, i-1)
        
        time_vector.append(motion.getStateVector(i-1).getTime())
        
        for j, muscle_name in enumerate(muscle_names):
            moment_arm = model.getMuscles().get(muscle_name).computeMomentArm(state, coordSet.get(Index))
            moment_arms[muscle_name] = moment_arms.get(muscle_name, []) + [moment_arm]

        print(f'frame {i} took {time.time() - initial_time:.6f} seconds')
        
    # make a dataframe
    df = pd.DataFrame(moment_arms, index=time_vector)
    df.index.name = 'Time'
    df.columns.name = 'Muscles'
    breakpoint()

    # compute moment arms for each muscle and create time vector
    time_vector = []
    for i in range(1, motion.getSize()):
        
        flexAngleL = motion.getStateVector(i-1).getData().get(flexIndexL) / 180 * np.pi
        rotAngleL = motion.getStateVector(i-1).getData().get(rotIndexL) / 180 * np.pi
        addAngleL = motion.getStateVector(i-1).getData().get(addIndexL) / 180 * np.pi
        flexAngleLknee = motion.getStateVector(i-1).getData().get(flexIndexLknee) / 180 * np.pi
        flexAngleLank = motion.getStateVector(i-1).getData().get(flexIndexLank) / 180 * np.pi

        time_vector.append(motion.getStateVector(i-1).getTime())
        # Update the state with the joint angle
        coordSet = model.updCoordinateSet()
        coordSet.get(flexIndexL).setValue(state, flexAngleL)
        coordSet.get(rotIndexL).setValue(state, rotAngleL)
        coordSet.get(addIndexL).setValue(state, addAngleL)
        coordSet.get(flexIndexLknee).setValue(state, flexAngleLknee)
        coordSet.get(flexIndexLank).setValue(state, flexAngleLank)

        # Realize the state to compute dependent quantities
        model.computeStateVariableDerivatives(state)
        model.realizeVelocity(state)

        # Compute the moment arm hip
        for j in range(len(muscleIndices_hip)):
            muscleIndex = muscleIndices_hip[j]
            if muscleNames_hip[j][-1] == leg:
                flexMomentArm = model.getMuscles().get(muscleIndex).computeMomentArm(state, flexCoordL)
                flexMomentArms[i, j] = flexMomentArm

                rotMomentArm = model.getMuscles().get(muscleIndex).computeMomentArm(state, rotCoordL)
                rotMomentArms[i, j] = rotMomentArm

                addMomentArm = model.getMuscles().get(muscleIndex).computeMomentArm(state, addCoordL)
                addMomentArms[i, j] = addMomentArm

        # Compute the moment arm knee
        for j in range(len(muscleNames_knee)):
            muscleIndex = muscleIndices_knee[j]
            if muscleNames_knee[j][-1] == leg:
                kneeFlexMomentArm = model.getMuscles().get(muscleIndex).computeMomentArm(state, flexCoordLknee)
                kneeFlexMomentArms[i, j] = kneeFlexMomentArm

        # Compute the moment arm ankle
        for j in range(len(muscleNames_ankle)):
            muscleIndex = muscleIndices_ankle[j]
            if muscleNames_ankle[j][-1] == leg:
                ankleFlexMomentArm = model.getMuscles().get(muscleIndex).computeMomentArm(state, flexCoordLank)
                ankleFlexMomentArms[i, j] = ankleFlexMomentArm

    
    
    
    
    
    
    
    
    
    # coordinate names
    flexIndexL, flexCoordL = get_model_coord(model, 'hip_flexion_' + leg)
    rotIndexL, rotCoordL = get_model_coord(model, 'hip_rotation_' + leg)
    addIndexL, addCoordL = get_model_coord(model, 'hip_adduction_' + leg)
    flexIndexLknee, flexCoordLknee = get_model_coord(model, 'knee_angle_' + leg)
    addIndexLknee, addCoordLknee = get_model_coord(model, 'knee_adduction_' + leg)
    flexIndexLank, flexCoordLank = get_model_coord(model, 'ankle_angle_' + leg)

    # get names of the hip muscles
    numMuscles = model.getMuscles().getSize()
    muscleIndices_hip = []
    muscleNames_hip = []
    for i in range(numMuscles):
        tmp_muscleName = str(model.getMuscles().get(i).getName())
        breakpoint()
        muscle = model.getMuscles().get(i)
        if muscle_crosses_coordinate(osimModel, tmp_muscleName, flexCoordL.getName()) and ('_' + leg in tmp_muscleName):
            muscleIndices_hip.append(i)
            muscleNames_hip.append(tmp_muscleName)

    flexMomentArms = np.zeros((motion.getSize(), len(muscleIndices_hip)))
    addMomentArms = np.zeros((motion.getSize(), len(muscleIndices_hip)))
    rotMomentArms = np.zeros((motion.getSize(), len(muscleIndices_hip)))

    # get names of the knee muscles
    numMuscles = model.getMuscles().getSize()
    muscleIndices_knee = []
    muscleNames_knee = []
    for i in range(numMuscles):
        tmp_muscleName = str(model.getMuscles().get(i).getName())
        if ('bf' in tmp_muscleName or 'gas' in tmp_muscleName or 'grac' in tmp_muscleName or 'sart' in tmp_muscleName or
                'semim' in tmp_muscleName or 'semit' in tmp_muscleName or 'rec' in tmp_muscleName or 'vas' in tmp_muscleName) and ('_' + leg in tmp_muscleName):
            muscleIndices_knee.append(i)
            muscleNames_knee.append(tmp_muscleName)

    kneeFlexMomentArms = np.zeros((motion.getSize(), len(muscleIndices_knee)))

    # get names of the ankle muscles
    numMuscles = model.getMuscles().getSize()
    muscleIndices_ankle = []
    muscleNames_ankle = []
    for i in range(numMuscles):
        tmp_muscleName = str(model.getMuscles().get(i).getName())
        print(tmp_muscleName)
        if ('edl' in tmp_muscleName or 'ehl' in tmp_muscleName or 'tibant' in tmp_muscleName or 'gas' in tmp_muscleName or
                'fdl' in tmp_muscleName or 'fhl' in tmp_muscleName or 'perb' in tmp_muscleName or 'perl' in tmp_muscleName or
                'sole' in tmp_muscleName or 'tibpos' in tmp_muscleName) and ('_' + leg in tmp_muscleName):
            muscleIndices_ankle.append(i)
            muscleNames_ankle.append(tmp_muscleName)

    ankleFlexMomentArms = np.zeros((motion.getSize(), len(muscleIndices_ankle)))

    # compute moment arms for each muscle and create time vector
    time_vector = []
    for i in range(1, motion.getSize()):
        flexAngleL = motion.getStateVector(i-1).getData().get(flexIndexL) / 180 * np.pi
        rotAngleL = motion.getStateVector(i-1).getData().get(rotIndexL) / 180 * np.pi
        addAngleL = motion.getStateVector(i-1).getData().get(addIndexL) / 180 * np.pi
        flexAngleLknee = motion.getStateVector(i-1).getData().get(flexIndexLknee) / 180 * np.pi
        flexAngleLank = motion.getStateVector(i-1).getData().get(flexIndexLank) / 180 * np.pi

        time_vector.append(motion.getStateVector(i-1).getTime())
        # Update the state with the joint angle
        coordSet = model.updCoordinateSet()
        coordSet.get(flexIndexL).setValue(state, flexAngleL)
        coordSet.get(rotIndexL).setValue(state, rotAngleL)
        coordSet.get(addIndexL).setValue(state, addAngleL)
        coordSet.get(flexIndexLknee).setValue(state, flexAngleLknee)
        coordSet.get(flexIndexLank).setValue(state, flexAngleLank)

        # Realize the state to compute dependent quantities
        model.computeStateVariableDerivatives(state)
        model.realizeVelocity(state)

        # Compute the moment arm hip
        for j in range(len(muscleIndices_hip)):
            muscleIndex = muscleIndices_hip[j]
            if muscleNames_hip[j][-1] == leg:
                flexMomentArm = model.getMuscles().get(muscleIndex).computeMomentArm(state, flexCoordL)
                flexMomentArms[i, j] = flexMomentArm

                rotMomentArm = model.getMuscles().get(muscleIndex).computeMomentArm(state, rotCoordL)
                rotMomentArms[i, j] = rotMomentArm

                addMomentArm = model.getMuscles().get(muscleIndex).computeMomentArm(state, addCoordL)
                addMomentArms[i, j] = addMomentArm

        # Compute the moment arm knee
        for j in range(len(muscleNames_knee)):
            muscleIndex = muscleIndices_knee[j]
            if muscleNames_knee[j][-1] == leg:
                kneeFlexMomentArm = model.getMuscles().get(muscleIndex).computeMomentArm(state, flexCoordLknee)
                kneeFlexMomentArms[i, j] = kneeFlexMomentArm

        # Compute the moment arm ankle
        for j in range(len(muscleNames_ankle)):
            muscleIndex = muscleIndices_ankle[j]
            if muscleNames_ankle[j][-1] == leg:
                ankleFlexMomentArm = model.getMuscles().get(muscleIndex).computeMomentArm(state, flexCoordLank)
                ankleFlexMomentArms[i, j] = ankleFlexMomentArm

    # check discontinuities
    discontinuity = []
    muscle_action = []
    time_discontinuity = []

    fDistC = plt.figure('Discontinuity', figsize=(8, 8))
    plt.title(ik_output)

    save_folder = os.path.join(os.path.dirname(ik_output),'momentArmsCheck')

    def find_discontinuities(momArms, threshold, muscleNames, action, discontinuity, muscle_action, time_discontinuity):
        for i in range(momArms.shape[1]):
            dy = np.diff(momArms[:, i])
            discontinuity_indices = np.where(np.abs(dy) > threshold)[0]
            if discontinuity_indices.size > 0:
                print('Discontinuity detected at', muscleNames[i], 'at ', action, ' moment arm')
                plt.plot(momArms[:, i])
                plt.plot(discontinuity_indices, momArms[discontinuity_indices, i], 'rx')
                discontinuity.append(i)
                muscle_action.append(str(muscleNames[i] + ' ' + action + ' at frames: ' + str(discontinuity_indices)))
                time_discontinuity.append([time_vector[index] for index in discontinuity_indices])


        return discontinuity, muscle_action, time_discontinuity

    # hip flexion
    discontinuity, muscle_action, time_discontinuity = find_discontinuities(
        flexMomentArms, threshold, muscleNames_hip, 'flexion', discontinuity, muscle_action, time_discontinuity)

    # hip adduction
    discontinuity, muscle_action, time_discontinuity = find_discontinuities(
        addMomentArms, threshold, muscleNames_hip, 'adduction', discontinuity, muscle_action, time_discontinuity)
    
    # hip rotation
    discontinuity, muscle_action, time_discontinuity = find_discontinuities(
        rotMomentArms, threshold, muscleNames_hip, 'rotation', discontinuity, muscle_action, time_discontinuity)
    
    # knee flexion
    discontinuity, muscle_action, time_discontinuity = find_discontinuities(
        kneeFlexMomentArms, threshold, muscleNames_knee, 'flexion', discontinuity, muscle_action, time_discontinuity)
    
    # ankle flexion
    discontinuity, muscle_action, time_discontinuity = find_discontinuities(
        ankleFlexMomentArms, threshold, muscleNames_ankle, 'dorsiflexion', discontinuity, muscle_action, time_discontinuity)
    
    # plot discontinuities
    if len(discontinuity) > 0:
        plt.legend(muscle_action)
        plt.ylabel('Muscle Moment Arms with discontinuities (m)')
        plt.xlabel('Frame (after start time)')
        save_fig(plt.gcf(), save_path=os.path.join(save_folder, 'discontinuities_' + leg + '.png'))
        print('\n\nYou should alter the model - most probably you have to reduce the radius of corresponding wrap objects for the identified muscles\n\n\n')

        # save txt file with discontinuities
        with open(os.path.join(save_folder, 'discontinuities_' + leg + '.txt'), 'w') as f:
            f.write(f"model file = {osim_modelPath}\n")
            f.write(f"motion file = {ik_output}\n")
            f.write(f"leg checked = {leg}\n")
            
            f.write("\n muscles with discontinuities \n", ) 
            
            for i in range(len(muscle_action)):
                try:
                    f.write("%s : time %s \n" % (muscle_action[i], time_discontinuity[i]))
                except:
                    print('no discontinuities detected')

        momentArmsAreWrong = 1
    else:
        plt.close(fDistC)
        print('No discontinuities detected')
        momentArmsAreWrong = 0

    # plot hip flexion
    plt.figure('flexMomentArms_' + leg, figsize=(8, 8))
    plt.plot(flexMomentArms)
    plt.title('All muscle moment arms in motion ' + ik_output)
    plt.legend(muscleNames_hip, loc='best')
    plt.ylabel('Hip Flexion Moment Arm (m)')
    plt.xlabel('Frame (after start time)')
    utils.save_fig(plt.gcf(), save_path=os.path.join(save_folder, 'hip_flex_MomentArms_' + leg + '.png'))

    # hip adduction
    plt.figure('addMomentArms_' + leg, figsize=(8, 8))
    plt.plot(addMomentArms)
    plt.title('All muscle moment arms in motion ' + ik_output)
    plt.legend(muscleNames_hip, loc='best')
    plt.ylabel('Hip Adduction Moment Arm (m)')
    plt.xlabel('Frame (after start time)')
    utils.save_fig(plt.gcf(), save_path=os.path.join(save_folder, 'hip_add_MomentArms_' + leg + '.png'))

    # hip rotation
    plt.figure('rotMomentArms_' + leg, figsize=(8, 8))
    plt.plot(rotMomentArms)
    plt.title('All muscle moment arms in motion ' + ik_output)
    plt.legend(muscleNames_hip, loc='best')
    plt.ylabel('Hip Rotation Moment Arm (m)')
    plt.xlabel('Frame (after start time)')
    utils.save_fig(plt.gcf(), save_path=os.path.join(save_folder, 'hip_rot_MomentArms_' + leg + '.png'))

    # knee flexion
    plt.figure('kneeFlexMomentArms_' + leg, figsize=(8, 8))
    plt.plot(kneeFlexMomentArms)
    plt.title('All muscle moment arms in motion ' + ik_output)
    plt.legend(muscleNames_knee, loc='best')
    plt.ylabel('Knee Flexion Moment Arm (m)')
    plt.xlabel('Frame (after start time)')
    utils.save_fig(plt.gcf(), save_path=os.path.join(save_folder, 'knee_MomentArms_' + leg + '.png'))

    # ankle flexion
    plt.figure('ankleFlexMomentArms_' + leg, figsize=(8, 8))
    plt.plot(ankleFlexMomentArms)
    plt.title('All muscle moment arms in motion ' + ik_output)
    plt.legend(muscleNames_ankle, loc='best')
    plt.ylabel('Ankle Dorsiflexion Moment Arm (m)')
    plt.xlabel('Frame (after start time)')
    utils.save_fig(plt.gcf(), save_path=os.path.join(save_folder, 'ankle_MomentArms_' + leg + '.png'))

    print('Moment arms checked for ' + ik_output)
    print('Results saved in ' + save_folder + ' \n\n' )

    return momentArmsAreWrong,  discontinuity, muscle_action



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
print(f"Muscles crossing hip_flexion_l: {muscles}")

checkMuscleMomentArms(osim_modelPath=osimModel,
                      ik_output=trial.outputFiles['IK'].abspath(),
                      leg='l',
                      threshold=0.005)
exit()
for muscle in muscles:
    muscle_name = muscle.getName()
    coordinates = coordinates_per_muscle(osimModel, muscle_name)
    print(f"Coordinates for muscle {muscle_name}: {coordinates}")

    moment_arms = checkMuscleMomentArms(osim_modelPath=osimModel,
                                        ik_output=trial.outputFiles['IK'].abspath(),
                                        leg='l',
                                        threshold=0.005)
    save_path = os.path.join(trial.path,'moment_arms' ,f"{muscle_name}.sto")
    utils.write_sto_file(moment_arms, save_path)
    print(f"Moment arms for muscle {muscle_name} saved to {save_path}")