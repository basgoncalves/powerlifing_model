
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

osimModel = osim.Model(trial.USED_MODEL)
ik_results = trial.outputFiles['IK'].abspath()
muscleAnalysis = trial.outputFiles['MA'].abspath()
dof = 'hip_flexion_r'

angles = utils.load_any_data_file(ik_results)
mom_arms = utils.load_any_data_file(os.path.join(muscleAnalysis, f'_MuscleAnalysis_Moment_{dof}.sto'))

# create top and bottom subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# plot joint angles
ax1.plot(angles['time'], angles[dof], label='Joint Angle')
ax1.set_ylabel('Angle (degrees)')
ax1.set_title(f'Joint Angle and Muscle Moment Arms for {dof}')
ax1.legend()
ax1.grid()

# plot moment arms
for muscle in mom_arms.columns:
    if 'time' in muscle.lower():
        continue
    ax2.plot(mom_arms['time'], mom_arms[muscle], label=muscle)
ax2.set_ylabel('Moment Arm (m)')
ax2.legend()
ax2.grid()

plt.xlabel('Time (s)')
plt.tight_layout()
plt.show()