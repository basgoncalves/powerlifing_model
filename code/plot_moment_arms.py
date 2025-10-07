
import os
from matplotlib import pyplot as plt
import opensim as osim
import utils
import paths

base_dir = paths.SIMULATION_DIR
subject = 'Athlete_03'  # Replace with actual subject name
session = '22_07_06'  # Replace with actual session name
trial = 'sq_70'  # Replace with actual trial name

# create a trial instance
trial = paths.Trial(subject_name=subject, session_name=session, trial_name=trial)
trial2 = paths.Trial(subject_name=subject, session_name=session, trial_name='sq_90')

fig, axes = trial.plot_moment_arms(coord_name='hip_flexion_r')
fig, axes = trial2.plot_moment_arms(coord_name='hip_flexion_r', fig=fig)
plt.show()
