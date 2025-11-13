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
    
    trial.scale_emg(scale_factor=0.70)
    # trial.create_ceinms_calibration_setup()
    # trial.create_ceinms_calibration_gfc()
    # trial.create_ceinms_input_data()
    
    # trial.run_ceinms_calibration()
    
    trial.run_ceinms_exe_loop()
    # trial.run_ceinms_exe()
    # trial.run_ceinms_optimise()
    
    # os.chdir(trial.path)
    # ceinms.plot_experimental_vs_ceinms(
    #     emgFile=trial.EMG_NORMALISED,
    #     ceinmsExcitationsFile=os.path.join(trial.path, 'Execution', 'AdjustedEmgs.sto'),
    #     excitationGeneratorFile=trial.CEINMS_EXCITATION_GENERATOR,
    #     externalMomentsFile=trial.ID,
    #     ceinmsTorquesFile=os.path.join(trial.path, 'Execution', 'Torques.sto')
    # )
    
    


            

