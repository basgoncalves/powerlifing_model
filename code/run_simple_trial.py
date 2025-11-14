import os
import ceinms
import utils
import settings
     

if __name__ == "__main__":
    
    trialPath = input("Please provide the path to the trial directory: ")
    
    analysis = utils.Analyse(trialPath)
    
    analysis.replace = True
    # analysis.run_ik()
    # analysis.run_id()
    # analysis.run_ma()
    # analysis.run_so()
    # analysis.run_jra()
    # analysis.run_emg_normalise()
    # analysis.scale_emg(scale_factor=0.70)
    # analysis.create_ceinms_input_data()
    # analysis.create_ceinms_exe_setup()
    # analysis.create_ceinms_exe_cfg()
    # # analysis.run_ceinms_exe_loop()
    # analysis.run_ceinms_exe()
    analysis.run_jra_ceinms()
    analysis.run_jra()
    
    analysis.push_trial_results_to_git()
    
    


            

