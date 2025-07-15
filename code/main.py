import os
import paths
import shutil
import utils
import run_ik, run_id, run_so, run_ma, copy_setups_to_trial

paths.print_settings()  # Print paths for debugging
continue_analysis = input("Continue with analysis? (y/n): ").strip().lower()

if continue_analysis != 'y':
    print("Analysis aborted by user.")
    exit()


# copy generic setups to trial directory
copy_setups_to_trial.run()

# 1. Scale the model

# 2. Run IK
if True:
    run_ik.run_IK(osim_modelPath=paths.USED_MODEL, marker_trc=paths.MARKERS_TRC,
              ik_output=paths.IK_OUTPUT, setup_xml=paths.SETUP_IK, time_range=paths.TIME_RANGE)

# 3. Run ID
if True:
    run_id.run_ID(osim_modelPath=paths.USED_MODEL, ik_mot=paths.IK_OUTPUT,
              grf_xml=paths.GRF_XML, setup_xml=paths.SETUP_ID)

# 4. Run muscle analysis
if True:
    run_ma.run_MA(osim_modelPath=paths.USED_MODEL, ik_output=paths.IK_OUTPUT,
              grf_xml=paths.GRF_XML, resultsDir=paths.MA_OUTPUT)

# 5. Run Static Optimization
if True:
    run_so.run_SO(osim_modelPath=paths.USED_MODEL, ik_output=paths.IK_OUTPUT,
              grf_xml=paths.GRF_XML, actuators=paths.ACTUATORS_SO, resultsDir=paths.SO_OUTPUT)
    
# 6. Run CEINMS calibration and optimization