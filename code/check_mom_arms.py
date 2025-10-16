import numpy as np
import opensim as osim
import utils
import os
import matplotlib.pyplot as plt
import paths

if __name__ == '__main__':
    
    subject = 'Athlete_03_MRI_BG'
    session = '22_07_06'
    trial_name = 'sq_80'
    trial = utils.Trial(subject_name=subject, session_name=session, trial_name=trial_name)
    osim_modelPath = trial.USED_MODEL
    ik_mot = trial.outputFiles['IK'].abspath()

    utils.print_to_log(f'Checking muscle moment arms for: {trial.subject} / {trial.session} / {trial.name}')

    # Run the Inverse Dynamics
    utils.checkMuscleMomentArms(osim_modelPath = osim_modelPath, 
                                ik_output = ik_mot, 
                                leg = 'l', 
                                threshold = 0.005)
    
    utils.checkMuscleMomentArms(osim_modelPath = osim_modelPath, 
                                ik_output = ik_mot, 
                                leg = 'r', 
                                threshold = 0.005)
    
    