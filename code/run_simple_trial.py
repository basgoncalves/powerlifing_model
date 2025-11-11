import os
import ceinms
import utils
import settings
     

if __name__ == "__main__":
    
    # trialPath = input("Please provide the path to the trial directory: ")
    # trial = utils.Analyse(trialPath)
    
    # trial.run_ik()
    # trial.run_id()
    # trial.run_ma()
    # trial.run_so()
    # trial.run_jra()
    
    # trial.create_ceinms_calibration_setup()
    # trial.create_ceinms_calibration_gfc()
    # trial.create_ceinms_input_data()
    # trial.run_ceinms_calibration()
    

    # trial.create_ceinms_optimise_setup()
    
    act = r"C:\Git\1_current_projects\powerlifing_model\simulations\012\pre\Run_baselineB1\Execution\AdjustedEmgs.sto"
    emg = r"C:\Git\1_current_projects\powerlifing_model\simulations\012\pre\Run_baselineB1\emg.mot"
    id = r"C:\Git\1_current_projects\powerlifing_model\simulations\012\pre\Run_baselineB1\inverse_dynamics.sto"
    troques = r"C:\Git\1_current_projects\powerlifing_model\simulations\012\pre\Run_baselineB1\Execution\Torques.sto"
    excgen = r"C:\Git\1_current_projects\powerlifing_model\simulations\012\pre\excitationGenerator.xml"
    ceinms.plot_experimental_vs_ceinms(emgFile=emg,
                                    ceinmsExcitationsFile=act,
                                    excitationGeneratorFile=excgen,
                                    externalMomentsFile=id,
                                    ceinmsTorquesFile=troques)
    

            

