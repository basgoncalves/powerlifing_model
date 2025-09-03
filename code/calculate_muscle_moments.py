from matplotlib import pyplot as plt
import paths
import os
import shutil
import utils
import pandas as pd

MUSCLE_MOMENTS_PREFIX = 'muscle_moments_'
MUSCLE_ANALYSIS_PREFIX = '_MuscleAnalysis_MomentArm_'

def main(muscleAnalysis_dir, muscleForces_filepath):
    '''
    Calculate the dot product between muscle forces and moment arms.
    '''
    
    muscleForces = utils.load_any_data_file(muscleForces_filepath)    
    
    # loop through all files in muscleAnalysis_dir containing 
    for root, dirs, files in os.walk(muscleAnalysis_dir):
        for filename in files:
            if MUSCLE_ANALYSIS_PREFIX in filename and MUSCLE_MOMENTS_PREFIX not in filename:
                file_path = os.path.join(root, filename)
                moment_arms = utils.load_any_data_file(file_path)
                
                if moment_arms is None:
                    breakpoint()
                    print(f"Could not load data from file: {file_path}")
                    continue
                
                # calculate muscle moments for all muscles
                muscle_moments = {}
                for muscle_name, force in muscleForces.items():
                    if 'time' in muscle_name.lower():
                        continue

                    # check if moment arm exists for muscle
                    if muscle_name not in moment_arms:
                        continue
                    
                    moment_arm = moment_arms[muscle_name]

                    # calculate muscle moment
                    muscle_moments[muscle_name] = force * moment_arm

                # save muscle moments to file
                df = pd.DataFrame(muscle_moments)
                # add time 
                df['time'] = muscleForces['time']
                output_file_path = os.path.join(root, f"{MUSCLE_MOMENTS_PREFIX}{filename}")
                utils.write_sto_file(df, output_file_path)

                print(f"Calculated muscle moments saved in {output_file_path}")

def groups_muscles(dataFrame, muscleMapping, type ='sum'):
    
    # find muscles not in mapping
    all_mapped_muscles = {muscle for muscle_group in muscleMapping.values() for muscle in muscle_group}
    unmapped_muscles = set(dataFrame.columns) - all_mapped_muscles
    
    muscleMapping_dof = muscleMapping.copy()
    # add as Others to mapping
    muscleMapping_dof['Others'] = []
    for muscle in unmapped_muscles:
        muscleMapping_dof['Others'].append(muscle)

    grouped = pd.DataFrame()
    for group, muscles in muscleMapping_dof.items():
        if type == 'sum':
            grouped[group] = dataFrame[muscles].sum(axis=1)
        elif type == 'mean':
            grouped[group] = dataFrame[muscles].mean(axis=1)

    # create a dict of line colors and line styles for when groups need to be plotted
    line_styles = {'R': {'linestyle': '-'},
                    'L': {'linestyle': '--'},
                    'O': {'linestyle': ':'}}
    
    # Group muscles by their base name (e.g., 'Adductors' for 'R Adductors' and 'L Adductors')
    muscle_groups = list(set(
        key.replace('R ', '').replace('L ', '') for key in muscleMapping_dof.keys()))
    
    # Create a color map for the base muscle groups
    colors = plt.colormaps.get_cmap('tab20')
    line_colors = {group: {'color': colors(i)} for i, group in enumerate(muscle_groups)}
    for i, group in enumerate(muscleMapping_dof.keys()):

        muscle = group.replace('R ', '').replace('L ', '')
        muscle_list = muscleMapping_dof[group]
        leg = group[0]
        style = line_styles[leg]['linestyle']
        color = line_colors[muscle]['color']
        muscleMapping_dof[group] = {'muscles': muscle_list, 'color': color, 'linestyle': style}

    return grouped, muscleMapping_dof

def plot(muscleAnalysis_dir, jointMomentsPath, muscleMapping):
    import matplotlib.pyplot as plt

    muscle_moments_files = []
    for root, dirs, files in os.walk(muscleAnalysis_dir):
        for filename in files:
            if filename.startswith(MUSCLE_MOMENTS_PREFIX):
                muscle_moments_files.append(os.path.join(root, filename))

    if not muscle_moments_files:
        print("No muscle moments files found")
        return

    # load joint moments
    jointMoments_df = utils.load_any_data_file(jointMomentsPath)
    jointMoments_df = utils.time_normalise_df(jointMoments_df)
    # Plot each muscle moments file
    for file_path in muscle_moments_files:
        
        fileName = os.path.basename(file_path)
        dof = fileName.replace(MUSCLE_ANALYSIS_PREFIX, '').replace(MUSCLE_MOMENTS_PREFIX, '').replace('.sto', '')        

        muscleMoment_df = utils.load_any_data_file(file_path)
        muscleMoment_df = utils.time_normalise_df(muscleMoment_df)
        
        try:
            jointMoment_dof = jointMoments_df[dof + '_moment']
        except:
            continue

        try:
            muscleMoment_df,muscleMapping_dof = groups_muscles(muscleMoment_df, muscleMapping)
        except:
            breakpoint()
            continue

        if muscleMoment_df is None:
            continue
        
        plt.figure(figsize=(12, 8))
        
        # Plot each muscle's moment
        for muscleGroup in muscleMapping_dof.keys():
            if 'time' not in muscleGroup.lower():
                style = muscleMapping_dof[muscleGroup]['linestyle']
                color = muscleMapping_dof[muscleGroup]['color']
                plt.plot(muscleMoment_df.index, muscleMoment_df[muscleGroup], label=muscleGroup,
                         linestyle=style, color=color)
        
        # Plot joint moments for comparison as a grey shade
        # breakpoint()
        plt.fill_between(jointMoment_dof.index, 
                         jointMoment_dof,
                         color='grey', alpha=0.3, label='Net moment')

        plt.xlabel('Time')
        plt.ylabel('Muscle Moment (Nm)')
        plt.title(f'Muscle Moments - {os.path.basename(file_path)}')
        # Adjust subplot parameters to make room for the legend
        plt.subplots_adjust(right=0.75)
        plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left', borderaxespad=0.)
        
        plt.grid(True)
        plt.tight_layout()
        
        output_filename = f"plot_{os.path.splitext(os.path.basename(file_path))[0]}.png"
        output_filepath = os.path.join(os.path.dirname(file_path), output_filename)
        plt.savefig(output_filepath)
        # breakpoint()
        print(f"Saved plot for file: {output_filepath}")
        plt.close()

if __name__ == '__main__':
   
    base_dir = paths.SIMULATION_DIR
    subject = 'Athlete_03_MRI'  # Replace with actual subject name
    session = '22_07_06'  # Replace with actual session name
    trial = 'sq_75'  # Replace with actual trial name
    
    # create a trial instance
    trial = paths.Trial(subject_name=subject, session_name=session, trial_name=trial)

    musicAnalysis_dir = trial.path + '\\' + trial.outputFiles['MA'].output
    muscleForces_filepath = trial.outputFiles['FORCES_SO'].abspath()
    muscleMapping = paths.Settings().Muscle_Groups
    idOutput = trial.outputFiles['ID'].abspath()

    if True:
        main(muscleAnalysis_dir=musicAnalysis_dir,
             muscleForces_filepath=muscleForces_filepath)
    
    if True:
        plot(muscleAnalysis_dir=musicAnalysis_dir, 
             jointMomentsPath=idOutput,
             muscleMapping=muscleMapping)