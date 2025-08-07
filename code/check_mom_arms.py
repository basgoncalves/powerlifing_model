import numpy as np
import opensim as osim
import utils
import os
import matplotlib.pyplot as plt
import paths

if __name__ == '__main__':
    
    subject = 'Katya_01'
    session = 'session1'
    trial_name = 'files_in_run01'
    trial = paths.Trial(subject_name=subject, session_name=session, trial_name=trial_name)
    
    

    utils.print_to_log(f'Checking muscle moment arms for: {paths.SUBJECT} / {paths.TRIAL_NAME} / {osim_modelPath}')

    # Run the Inverse Dynamics
    utils.checkMuscleMomentArms(osim_modelPath = osim_modelPath, 
                                ik_output = ik_mot, 
                                leg = 'l', 
                                threshold = 0.005)
    
    utils.checkMuscleMomentArms(osim_modelPath = osim_modelPath, 
                                ik_output = ik_mot, 
                                leg = 'r', 
                                threshold = 0.005)
    
    utils.print_to_log(f'Muscle moment saved to: {os.path.dirname(paths.IK_OUTPUT)}')