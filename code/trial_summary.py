import os
import utils
import settings
import matplotlib.pyplot as plt

def trialSummary(trial: utils.Trial, variable):
     """Summarizes trials based on predefined settings."""
     summary = {}
     trial.load_outputs()
     breakpoint()
     return summary

if __name__ == "__main__":
    trial_List = []
    while True:
        user_input = input("Enter trial path (or 'enter' to continue): ").strip('"')
        if user_input == "":
            break
        trial_List.append(user_input)

    for trial_path in trial_List:
        trial = utils.Trial(subject_name=trial_path)
        breakpoint()
        summary = trialSummary(trial)
    
    # plot each variable in summary
    for variable, data in summary.items():
        
        columns = list(data.values())[0].columns
        nRows = (len(columns) + 1) // 2
        nCols = 2
        fig, axs = plt.subplots(nRows, nCols, figsize=(12, 12))
        fig.suptitle(f"Summary for {variable}")
        axs = axs.flatten()
        for i, col in enumerate(columns):
            breakpoint()
            axs[i].plot(data['Time'], data[col], label=variable)
            axs[i].set_title(col)
            axs[i].set_xlabel("Normalized Time (%)")
        
        axs[0].legend()
        breakpoint()
            

