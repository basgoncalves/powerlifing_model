import os
import utils
import settings
import matplotlib.pyplot as plt

def trialSummary(trialPathsList, variable):
     """Summarizes trials based on predefined settings."""
     summary = {}
     for trialPath   in trialPathsList:
         sep = os.path.sep
         # load data files
         ik = utils.load_any_data_file(trialPath + sep + settings.Outputs().IK)
         id = utils.load_any_data_file(trialPath + sep + settings.Outputs().ID)
         muscleActivations = utils.load_any_data_file(trialPath + sep + settings.Outputs().SO_activations)
         muscleForces = utils.load_any_data_file(trialPath + sep + settings.Outputs().SO_forces)
         jrl = utils.load_any_data_file(trialPath + sep + settings.Outputs().JRA)

         # summarize data
         summary[trialPath] = {
             "IK": utils.time_normalise_df(ik),
             "ID": utils.time_normalise_df(id),
             "Muscle Activations": utils.time_normalise_df(muscleActivations),
             "Muscle Forces": utils.time_normalise_df(muscleForces),
             "Joint Reaction Loads": utils.time_normalise_df(jrl)
         }

     return summary

if __name__ == "__main__":
    trial_List = []
    while True:
        user_input = input("Enter trial name (or 'enter' to continue): ").strip('"')
        if user_input == "":
            break
        trial_List.append(user_input)

    summary = trialSummary(trial_List, variable)
    
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
            

