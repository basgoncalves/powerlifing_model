import os
import subprocess
from xml.etree import ElementTree as ET
import time
import utils
import openSim
import ceinms
import exportC3D

trialPath = os.path.join(utils.SIMULATIONS_DIR, 'Athlete_03_MRI_BG', '25_03_31', 'Squat_bw_01') # Walking_02, Squat_35kg_01
print(f'Analyzing trial at path: {trialPath}')

analysis = utils.Analyse(trialPath)
# analysis.reset_settings_xml()
# print main inputs
print("Main inputs:")
print(f"Model file: {analysis.model_dir}")
print(f"time range: {analysis.time_range}")
print(f"IK file: {analysis.ik}")

analysis.push_trial_results_to_git()