import os
import utils
import settings
import matplotlib.pyplot as plt

def trialSummary(trial: utils.Trial):
     """Summarizes trials based on predefined settings."""
     trial.plot_summary()
     
     

if __name__ == "__main__":
    trial_List = []

    for subject in settings.SUBJECTS_TO_ANALYSE:
        for session in settings.SESSIONS_TO_ANALYSE:
            for trial in settings.TRIALS_TO_ANALYSE:
                trial_path = os.path.join(settings.SIMULATIONS_DIR, subject, session, trial)
                if os.path.exists(trial_path):
                    trial_List.append(trial_path)

    for trial_path in trial_List:
        trial = utils.Trial(subject_name=trial_path)
        summary = trialSummary(trial)
        print(f"Summary for trial {trial.name} completed.")
            

