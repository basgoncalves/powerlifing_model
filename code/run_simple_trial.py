import os
import ceinms
import utils
import settings
     

if __name__ == "__main__":
    
    trialPath = input("Please provide the path to the trial directory: ")
    trial = utils.Analyse(trialPath)
    
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
    
    act = trial.CEINMS_OPTIMISATION_DIR + os.sep + "AdjustedEmgs.sto"
    emg = trial.path + os.sep + trial.EMG_NORMALISED
    id = trial.path + os.sep + trial.ID
    troques = trial.CEINMS_OPTIMISATION_DIR + os.sep + "Torques.sto"
    excgen = trial.CEINMS_EXCITATION_GENERATOR
    ceinms.plot_experimental_vs_ceinms(emgFile=emg,
                                    ceinmsExcitationsFile=act,
                                    excitationGeneratorFile=excgen,
                                    externalMomentsFile=id,
                                    ceinmsTorquesFile=troques)
    

            

