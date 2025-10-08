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
        muscle_names = muscles_per_coordinate(model, Coord.getName())
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
   
def create_nice_figure(n_subplots, figsize=(10, 5)):
    '''function to make a nice figure with subplots that are nicely arranged without 
    extra axes unused'''
    
    # make a square of subplots
    n_cols = int(np.ceil(np.sqrt(n_subplots)))
    n_rows = int(np.ceil(n_subplots / n_cols))

    fig, axs = plt.subplots(n_rows, n_cols, figsize=figsize)
    return fig, axs

def mmfn(fig):
    '''make matplotlib figure nice'''
    # tight layout
    fig.tight_layout(pad=3.0)
    # set background to white
    fig.patch.set_facecolor('white')
    
    # make sure subplots and ticks don't overlap
    plt.subplots_adjust(hspace=0.4, wspace=0.4)   

def compareModels_rest(osimModelPath1, osimModelPath2, coordinate_list, plotType = 'bar'):
    model1 = osim.Model(osimModelPath1)
    model2 = osim.Model(osimModelPath2)
    
    state1 = model1.initSystem()
    state2 = model2.initSystem()
    
    coordSet1 = model1.getCoordinateSet()
    coordSet2 = model2.getCoordinateSet()
    
    # create subplot for each coordinate
    fig, axs = create_nice_figure(len(coordinate_list), figsize=(15, 10))

    for coord_idx, coord_name in enumerate(coordinate_list):
        
        muscles1 = muscles_per_coordinate(model1, coord_name)
        muscles2 = muscles_per_coordinate(model2, coord_name)

        # calculate moment arms for each muscle in both models
        muscles_common = set(muscles1).intersection(set(muscles2))
        for muscle in muscles_common: 
            moment_arm1 = model1.getMuscles().get(muscle).computeMomentArm(state1, coordSet1.get(coord_name))
            moment_arm2 = model2.getMuscles().get(muscle).computeMomentArm(state2, coordSet2.get(coord_name))
            
            # 2 bar plots
            if plotType == 'bar':
                ax = axs.flat[coord_idx]
                # Get or initialize the muscle position counter
                if not hasattr(ax, '_muscle_positions'):
                    ax._muscle_positions = {}
                    ax._x_pos = 0
                
                # Get position for this muscle (or create new one)
                if muscle not in ax._muscle_positions:
                    ax._muscle_positions[muscle] = ax._x_pos
                    ax._x_pos += 1
                
                x_pos = ax._muscle_positions[muscle]
                width = 0.35
                
                # Plot bars side by side
                ax.bar(x_pos - width/2, moment_arm1, width, color='b', alpha=0.6)
                ax.bar(x_pos + width/2, moment_arm2, width, color='r', alpha=0.6)
                
                # Set x-ticks and labels after all muscles are plotted
                if muscle == list(muscles_common)[-1]:  # Last muscle
                    positions = [ax._muscle_positions[m] for m in muscles_common]
                    ax.set_xticks(positions)
                    ax.set_xticklabels(list(muscles_common))

            elif plotType == 'line':
                ax = axs.flat[coord_idx]
                ax.plot([muscle + '_model1'], [moment_arm1], color='b', marker='o')
                ax.plot([muscle + '_model2'], [moment_arm2], color='r', marker='o')
            elif plotType == 'spider':
                ax = axs.flat[coord_idx]

                # Create lists to store all muscle data for this coordinate
                muscle_list = list(muscles_common)
                model1_values = []
                model2_values = []
                
                # Get moment arms for all muscles
                for muscle in muscle_list:
                    ma1 = model1.getMuscles().get(muscle).computeMomentArm(state1, coordSet1.get(coord_name))
                    ma2 = model2.getMuscles().get(muscle).computeMomentArm(state2, coordSet2.get(coord_name))
                    model1_values.append(ma1)
                    model2_values.append(ma2)
                
                # Create angles for each muscle
                angles = np.linspace(0, 2 * np.pi, len(muscle_list), endpoint=False).tolist()
                
                # Close the plot by adding first values at the end
                model1_values += model1_values[:1]
                model2_values += model2_values[:1]
                angles += angles[:1]
                
                # Create polar subplot
                ax = plt.subplot(len(coordinate_list)//2 + 1, 2, coord_idx + 1, polar=True)
                
                # Plot both models as separate rings
                ax.fill(angles, model1_values, color='b', alpha=0.25, label=model1.getName())
                ax.plot(angles, model1_values, color='b', marker='o')
                
                ax.fill(angles, model2_values, color='r', alpha=0.25, label=model2.getName())
                ax.plot(angles, model2_values, color='r', marker='s')
                
                # Set labels
                ax.set_xticks(angles[:-1])
                ax.set_xticklabels(muscle_list)

        ax.set_title(f'Coordinate: {coord_name}')
        ax.set_ylabel('Moment Arm (m)')
        
        if len(muscles_common) > 5:
            plt.setp(ax.get_xticklabels(), rotation=75, ha='right')
    
    # select only first ax
    ax = axs.flat[0]
    
    if plotType in ['bar', 'line']:
        ax.legend([model1.getName(), model2.getName()])
        # rotate xtick labels if too many
        
    elif plotType == 'spider':# legend only 2 entries one for red and one for blue (1st and 3rd entry)
        handles, labels = ax.get_legend_handles_labels()
        blue_handle = next((h for h, l in zip(handles, labels) if l == model1.getName()), None)
        red_handle = next((h for h, l in zip(handles, labels) if l == model2.getName()), None)
        ax.legend([blue_handle, red_handle], [labels[0], labels[2]], loc='upper right', bbox_to_anchor=(1.1, 1.1))

    
    # ask user where to save
    save_path = input('Enter path to save figure (including filename, e.g. C:/path/figure.png): ').strip().strip('"')
    fig.savefig(save_path)
    print(f'Figure saved to {save_path}')
     
if __name__ == "__main__":
    base_dir = paths.SIMULATION_DIR
    subject = 'Athlete_03'  # Replace with actual subject name
    session = '22_07_06'  # Replace with actual session name
    trial = 'sq_70'  # Replace with actual trial name

    # create a trial instance
    trial = paths.Trial(subject_name=subject, session_name=session, trial_name=trial)
    
    coordinates_to_check = ['hip_flexion_l', 'hip_flexion_r',
                            'knee_angle_l', 'knee_angle_r',
                            'ankle_angle_l', 'ankle_angle_r']

    if False:    
        osimModel = osim.Model(trial.USED_MODEL)
        muscles = osimModel.getMuscles()
        joint_angles = osim.Storage(trial.outputFiles['IK'].abspath())

        muscles = muscles_per_coordinate(osimModel, coord_name='hip_flexion_l')
        checkMuscleMomentArms(osim_modelPath=osimModel,
                        ik_output=trial.outputFiles['IK'].abspath(),
                        threshold=0.005, 
                        coordinate_list=coordinates_to_check)

    if True:
        osimModelPath1 = input('Path to generic model: ').strip().strip('"')
        osimModelPath2 = input('Path to personalized model: ').strip().strip('"')
        compareModels_rest(osimModelPath1=osimModelPath1,
                        osimModelPath2=osimModelPath2,
                        coordinate_list=coordinates_to_check)