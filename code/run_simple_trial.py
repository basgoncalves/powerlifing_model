import os
import utils
import settings
     

if __name__ == "__main__":
    
    trialPath = input("Please provide the path to the trial directory: ")
    trial = utils.Analyse(trialPath)
    
    trial.create_ceinms_optimise_setup()
    trial.run_ceinms_optimise()
    
            

