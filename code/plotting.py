import os

import pandas as pd 
import paths



def add_df_to_plot(df, ax, label=None, color=None, linestyle='-', marker=None):
    """
    Adds a DataFrame to a plot with specified aesthetics.
    
    Parameters:
        df (pd.DataFrame): DataFrame containing data to plot.
        ax (matplotlib.axes.Axes): Axes object to plot on.
        label (str): Label for the plot legend.
        color (str): Color of the plot line.
        linestyle (str): Style of the line (e.g., '-', '--').
        marker (str): Marker style for the data points.
    """
    if df.empty:
        print("Warning: Attempted to plot an empty DataFrame.")
        return
    
    df.plot(ax=ax, label=label, color=color, linestyle=linestyle, marker=marker)
    if label:
        ax.legend()

def main():
    """
    Main function to demonstrate the usage of add_df_to_plot.
    This is a placeholder for actual plotting logic.
    """
    import pandas as pd
    import matplotlib.pyplot as plt
    
    # Example DataFrame
    data = {
        'Time': [0, 1, 2, 3, 4],
        'Force': [0, 10, 20, 15, 5]
    }
    df = pd.DataFrame(data).set_index('Time')
    
    # Create a plot
    fig, ax = plt.subplots()
    
    # Add DataFrame to plot
    add_df_to_plot(df, ax, label='Force over Time', color='blue', linestyle='-', marker='o')
    
    # Show the plot
    plt.show()
    
if __name__ == "__main__":
    
    exit
    dataset = dict()
    for subject in paths.Analysis().SUBJECTS:
        
        subject_data = pd.DataFrame()
        subject_data['name'] = subject.name
        dataset[subject.name] = subject_data.copy()
        
        print(f"Processing subject: {subject.name}")
        for session in subject.SESSIONS:
            print(f"Processing session: {session.name}")
            for trial in session.TRIALS:
                print(f"Processing trial: {trial.name}")

    trialsList = {'MRI': ['sq_90_MRI', 'sq_70_MRI'],
                'EMG': ['sq_90_EMG', 'sq_70_EMG']}
    
    
    import compare_all_files_trials as compare_all
    import utils
    import paths
    
    subject = paths.Analysis().get_subject('Athlete_03') 

    trialsList = {
        'MRI': ['sq_90', 'sq_70'],
        'Linear': ['sq_90', 'sq_70']
    }
    
    for session, trials in trialsList.items():
        print(f"Processing session: {session}")
        for trial in trials:
            print(f"Processing trial: {trial}")
            compare_all.main(
                subject=subject,
                session=session,
                trial=trial,
                resultsDir=paths.RESULTS_DIR
            )
    compare_all.main(
        subject=subject,
               
    
    