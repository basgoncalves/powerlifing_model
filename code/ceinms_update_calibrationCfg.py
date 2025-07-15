import os 
import paths
import utils

if __name__ == "__main__":
    
    ceinmsCfg_path = input("Enter the path to the CEINMS calibration configuration file: ")
    if not os.path.exists(ceinmsCfg_path):
        raise FileNotFoundError(f"CEINMS calibration configuration file not found: {ceinmsCfg_path}")
    
    cfg = utils.read_xml(ceinmsCfg_path)
    trialSet = cfg.find('trialSet')
    trialSet.text = os.path.relpath(paths.CEINMS_INPUT_DATA, 
                                     start = os.path.dirname(ceinmsCfg_path))
    
    # save the modified configuration file
    utils.save_pretty_xml(cfg, ceinmsCfg_path)
    print(f"CEINMS calibration configuration updated and saved to: {ceinmsCfg_path}")
    