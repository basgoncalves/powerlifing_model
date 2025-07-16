import os
import paths
import shutil
import utils
import run_ik, run_id, run_so, run_ma, run_jra, copy_setups_to_trial, check_mom_arms

utils.print_to_log("Starting analysis...")
paths.print_settings()  # Print paths for debugging
continue_analysis = input("Continue with analysis? (y/n): ").strip().lower()

if continue_analysis != 'y':
    print("Analysis aborted by user.")
    utils.print_to_log("Analysis aborted by user.")
    exit()

utils.print_to_log(f'Running analysis on: {paths.SUBJECT} / {paths.TRIAL_NAME} / {paths.USED_MODEL}')

# copy generic setups to trial directory
if False:
    copy_setups_to_trial.run()

# 1. Scale the model

# 1b Change model muscle maximum isometric force
if False:
    factor = 3.0  # Increase by 3 times
    utils.increase_muscle_force(osim_file=paths.SCALED_MODEL_INCREASED_FORCE, 
                                factor=factor)
    
    utils.increase_muscle_force(osim_file=paths.MRI_MODEL_INCREASED_FORCE,
                                factor=factor)

# 2. Run IK
if True:
    utils.print_to_log(f'Running Inverse Kinematics on: {paths.SUBJECT} / {paths.TRIAL_NAME} / {paths.USED_MODEL}')
    run_ik.run_IK(osim_modelPath=paths.USED_MODEL, 
                  marker_trc=paths.MARKERS_TRC,
                  ik_output=paths.IK_OUTPUT, 
                  setup_xml=paths.SETUP_IK, 
                  time_range=paths.TIME_RANGE)
    utils.print_to_log(f'Inverse Kinematics completed. Results are saved in {paths.IK_OUTPUT}')

# 3. Run ID
if True:
    utils.print_to_log(f'Running Inverse Dynamics on: {paths.SUBJECT} / {paths.TRIAL_NAME} / {paths.USED_MODEL}')
    run_id.run_ID(osim_modelPath=paths.USED_MODEL, 
                  ik_mot=paths.IK_OUTPUT,
                  grf_xml=paths.GRF_XML, 
                  setup_xml=paths.SETUP_ID)
    utils.print_to_log(f'Inverse Dynamics completed. Results are saved in {paths.ID_OUTPUT}')

# 4. Run muscle analysis
if True:
    utils.print_to_log(f'Running Muscle Analysis on: {paths.SUBJECT} / {paths.TRIAL_NAME} / {paths.USED_MODEL}')
    run_ma.run_MA(osim_modelPath=paths.USED_MODEL, 
                  ik_output=paths.IK_OUTPUT,
                  grf_xml=paths.GRF_XML, 
                  resultsDir=paths.MA_OUTPUT)
    utils.print_to_log(f'Muscle Analysis completed. Results are saved in {paths.MA_OUTPUT}')
    
# 4b Check moment arms
if True:
    utils.print_to_log(f'Checking muscle moment arms for model: {paths.USED_MODEL}')
    utils.checkMuscleMomentArms(osim_modelPath=paths.USED_MODEL, 
                                ik_output=paths.IK_OUTPUT,
                                leg='l', 
                                threshold=0.005)
    utils.checkMuscleMomentArms(osim_modelPath=paths.USED_MODEL,
                                ik_output=paths.IK_OUTPUT, 
                                leg='r', 
                                threshold=0.005)
    utils.print_to_log(f'Muscle moment arms saved to: {os.path.dirname(paths.IK_OUTPUT)}')

# 5. Run Static Optimization
if True:
    utils.print_to_log(f'Running Static Optimization on: {paths.SUBJECT} / {paths.TRIAL_NAME} / {paths.USED_MODEL}')
    run_so.run_SO(osim_modelPath=paths.USED_MODEL, 
                  ik_output=paths.IK_OUTPUT,
                  grf_xml=paths.GRF_XML, 
                  actuators=paths.ACTUATORS_SO, 
                  resultsDir=paths.SO_OUTPUT)
    utils.print_to_log(f'Static Optimization completed. Results are saved in {paths.SO_OUTPUT}')
    
# 6 run Joint Reaction Analysis
if True:
    if True:
        utils.print_to_log(f'Running JRA on: {paths.SUBJECT} / {paths.TRIAL_NAME} / {paths.USED_MODEL}')
        run_jra.run_jra(modelpath=paths.USED_MODEL, 
                        coordinates_file=paths.IK_OUTPUT, 
                        externalloadsfile=paths.GRF_XML,
                        setupJRA=paths.SETUP_JRA,
                        actuators=None,
                        muscle_forces=paths.FORCES_OUTPUT, 
                        results_directory=os.path.dirname(paths.JRA_OUTPUT))

    if False:
        run_jra.run_jra_setup(modelpath=paths.USED_MODEL, 
                              setupJRA=paths.SETUP_JRA)
    
    utils.print_to_log(f'JRA completed. Results are saved in {os.path.dirname(paths.JRA_OUTPUT)}')


# 6. Run CEINMS calibration and optimization