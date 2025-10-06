import os
import time
import utils
import paths

def main(trial1: paths.Trial, trial2: paths.Trial):
    
    if True:
        try:
            trial1.compare_with(trial2)
        except Exception as e:
            print(f"Error during plotting: {e}")
            utils.print_to_log(f'Error during plotting: {e}')
    
if __name__ == "__main__":
    utils.print_to_log("Starting analysis...")
    
    start_time = time.time()
    settings = paths.Settings()
    settings._print()
    
    
    trial1 = paths.Trial(subject='Athlete_03', session='22_06_07', trial_name='sq_70')
    trial2 = paths.Trial(subject='Athlete_03_MRI', session='22_06_07', trial_name='sq_80')


    main(trial1=trial1, trial2=trial2)

    end_time = time.time()
    elapsed_time = end_time - start_time
    utils.print_to_log(f"Total analysis time: {elapsed_time:.2f} seconds \n \n")
    
