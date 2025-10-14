import os
import shutil
import time
from matplotlib import pyplot as plt
import pandas as pd
import opensim as osim

try:
    import utils
except ImportError:
    from . import utils
import math

#%% Folder stuctures should be: 
# powerlifitng_model
#   code/
#     setupFiles/
#       Rajagopal/
#       Purzel/
#          setup_IK.xml
#          setup_ID.xml 
#          setup_MA.xml
#          setup_SO.xml
#          externalloads.xml    
#          ...
#     executables/
#       CEINMS.exe
#       CEINMSoptimise.exe
#       ceinms-nn-calibrate.exe
#     paths.py
#     ceinms_muscle_groups_to_unCalibrated_model.py
#   models/
#     Athlete_03_linearly_scaled.osim
#     Athlete_03_mri_scaled.osim
#     Athlete_03_markerset.xml
#   simulations/
#     Athlete_03/
#       22_07_06/
#         sq_70_MRI/
#           c3dfile.c3d
#           events.csv
#           marker_experimental.trc
#           grf.mot
#           EMG_filtered.sto
#           externalloads.xml
# %% CODE and settings 

# Load settings from .json file
CODE = os.path.dirname(__file__)
SETUP_DIR = os.path.join(CODE, 'SetupFiles\Purzel')
POWERLIFTING_DIR = os.path.dirname(CODE)
MODELS_DIR = os.path.join(POWERLIFTING_DIR, 'models')

SIMULATION_DIR = os.path.join(POWERLIFTING_DIR, 'simulations')
RESULTS_DIR = os.path.join(POWERLIFTING_DIR, 'results')


#%% IF MAIN
if __name__ == "__main__":
    
    all_vars = {k: v for k, v in globals().items() if not k.startswith('_')}
    for var_name, var_value in all_vars.items():
        print(f"{var_name}: {var_value}")

# END