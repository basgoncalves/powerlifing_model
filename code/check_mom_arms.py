import numpy as np
import opensim as osim
import utils
import os
import matplotlib.pyplot as plt
import paths

if __name__ == '__main__':
    osim_modelPath = paths.USED_MODEL
    ik_mot = paths.IK_OUTPUT

    utils.print_to_log(f'Checking muscle moment arms for: {paths.SUBJECT} / {paths.TRIAL_NAME} / {osim_modelPath}')

    # Run the Inverse Dynamics
    utils.checkMuscleMomentArms(model_file_path = osim_modelPath, 
                                ik_file_path = ik_mot, 
                                leg = 'l', 
                                threshold = 0.005)
    
    utils.checkMuscleMomentArms(model_file_path = osim_modelPath, 
                                ik_file_path = ik_mot, 
                                leg = 'r', 
                                threshold = 0.005)
    
    utils.print_to_log(f'Muscle moment saved to: {os.path.dirname(paths.IK_OUTPUT)}')