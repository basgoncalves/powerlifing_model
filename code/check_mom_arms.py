import numpy as np
import opensim as osim
import utils
import os
import matplotlib.pyplot as plt

if __name__ == '__main__':
    
    trial_path = input("Please provide the path to the trial directory: ")  
    trial = utils.Analyse(trialPath=trial_path)
    osim_modelPath = trial.MODEL
    ik_mot = trial.IK

    utils.print_to_log(f'Checking muscle moment arms for: {trial_path}')

    # Run the Inverse Dynamics
    os.chdir(trial.path)
    utils.checkMuscleMomentArms(osim_modelPath = osim_modelPath, 
                                ik_output = ik_mot, 
                                leg = 'l', 
                                threshold = 0.005)
    
    os.chdir(trial.path)
    utils.checkMuscleMomentArms(osim_modelPath = osim_modelPath, 
                                ik_output = ik_mot, 
                                leg = 'r', 
                                threshold = 0.005)
    
    