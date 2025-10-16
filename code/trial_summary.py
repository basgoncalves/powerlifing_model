import os
import utils
import paths

def trialSummary(trial: utils.Trial):
     """Summarizes trials based on predefined settings."""
     
     # IK
     ik_results = utils.load_any_data_file(trial.outputFiles['IK'].abspath())

if __name__ == "__main__":
    
    settings = utils.Settings()
    analysis = utils.Analysis()
    
    for subject in analysis.SUBJECTS:
        for session in subject.SESSIONS:
            for trial in session.TRIALS:
                print(f"Processing Trial: {trial.trial_name} for Subject: {subject.subject_name}, Session: {session.session_name}")
                trialSummary()
                
                
