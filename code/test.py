import utils
import os

if __name__ == "__main__":


        subject  = 'Athlete_03_MRI_Katya' # Athlete_03_Lernagopal
        session = '25_03_31'
        trial = 'Squat_BW_02' #'Squat_BW_01' Squat_35kg_01 Walking_02
        analysis = utils.Analyse(trialPath=os.path.join(utils.SIMULATIONS_DIR, subject, session, trial))

        analysis.push_trial_results_to_git()