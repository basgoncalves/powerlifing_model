import os
import paths
import shutil


def run(replace = False):
    """
    Copies generic setup files to the trial directory.
    """
    if not os.path.exists(paths.TRIAL_DIR):
        os.makedirs(paths.TRIAL_DIR)
    
    # Copy generic setup files to the trial directory
    for key, value in paths.__dict__.items():
        if key.startswith('GENERIC'):
            dest_path = os.path.join(paths.TRIAL_DIR, os.path.basename(value))
            if not os.path.exists(dest_path) or replace:
                shutil.copy(value, dest_path)
                print(f"Copied {key} to {dest_path}")
            else:
                print(f"{dest_path} already exists, skipping copy for {key}")
    
    # Copy CEINMS files to the trial directory
    
    

if __name__ == "__main__":
    run()
