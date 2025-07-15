import os
import paths
import shutil


def run():
    """
    Copies generic setup files to the trial directory.
    """
    if not os.path.exists(paths.TRIAL_DIR):
        os.makedirs(paths.TRIAL_DIR)
    
    # Copy generic setup files to the trial directory
    for key, value in paths.__dict__.items():
        if key.startswith('GENERIC'):
            dest_path = os.path.join(paths.TRIAL_DIR, os.path.basename(value))
            shutil.copy(value, dest_path)
            print(f"Copied {key} to {dest_path}")
    
    # Copy CEINMS files to the trial directory
    