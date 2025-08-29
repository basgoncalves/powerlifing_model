import paths
import os
import shutil
import utils
import pandas as pd

MUSCLE_MOMENTS_PREFIX = 'muscle_moments_'
MUSCLE_ANALYSIS_PREFIX = '_MuscleAnalysis_Moment_'

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
                
def plot(muscleAnalysis_dir):
    import matplotlib.pyplot as plt

    muscle_moments_files = []
    for root, dirs, files in os.walk(muscleAnalysis_dir):
        for filename in files:
            if filename.startswith(MUSCLE_MOMENTS_PREFIX):
                muscle_moments_files.append(os.path.join(root, filename))

    if not muscle_moments_files:
        print("No muscle moments files found")
        return

    # Plot each muscle moments file
    for file_path in muscle_moments_files:
        
        df = utils.load_any_data_file(file_path)
        breakpoint()
        df = utils.time_normalise_df(df)

        if df is None:
            continue
        
        plt.figure(figsize=(12, 8))
        
        # Plot each muscle's moment
        for muscle in df.columns:
            if 'time' not in muscle.lower():
                plt.plot(df.index, df[muscle], label=muscle)
        
        plt.xlabel('Time')
        plt.ylabel('Muscle Moment (Nm)')
        plt.title(f'Muscle Moments - {os.path.basename(file_path)}')
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.grid(True)
        plt.tight_layout()

        plt.savefig(os.path.join(root, f"muscle_moments_{filename}.png"))

        print(f"Saved plot for file: {file_path}")

if __name__ == '__main__':
   
    base_dir = paths.SIMULATION_DIR
    subject = 'Athlete_03'  # Replace with actual subject name
    session = '22_07_06'  # Replace with actual session name
    trial = 'sq_70'  # Replace with actual trial name
    
    # create a trial instance
    trial = paths.Trial(subject_name=subject, session_name=session, trial_name=trial)

    musicAnalysis_dir = trial.path
    muscleForces_filepath = trial.outputFiles['FORCES_SO'].abspath()

    if True:
        main(muscleAnalysis_dir=musicAnalysis_dir,
             muscleForces_filepath=muscleForces_filepath)
    
    if False:
        plot(muscleAnalysis_dir=musicAnalysis_dir)