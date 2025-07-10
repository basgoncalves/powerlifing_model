from tps import ThinPlateSpline
from tps_scripts import *
import msk_modelling_python as msk


# Utilities 
def dirUp(path, levels=1):
    """
    Move up the directory structure by a specified number of levels.
    """
    for _ in range(levels):
        path = os.path.dirname(path)
    return path


def tps_2_0():
    print("Running TPS 2.0 script...")
    msk.time.sleep(1)
    
    

if __name__ == "__main__":
    mri_dir = os.path.abspath('../../MRI/results')
    path_to_json = os.path.join(mri_dir, 'orientation.mrk.json')
    models_dir = os.path.abspath('../../../../')
    print(f"Root directory for MRI: {models_dir}")
    xml_path = os.path.join(models_dir, 'Geometry', 'tps_warping.xml')
    osim_path = r"E:\DataFolder\AlexP\models\Athlete_03_lowerBody_final_increased_3.00.osim"
    working_dir = os.getcwd()
    output_path = os.path.join(working_dir, 'tps_warping_results')

    vtp_path = os.path.join(working_dir, 'Geometry')

    # check if paths exist
    if not os.path.exists(mri_dir):
        print(f"Directory {mri_dir} does not exist.")

    if not os.path.exists(path_to_json):
        print(f"File {path_to_json} does not exist.")
        
    if not os.path.exists(xml_path):
        print(f"File {xml_path} does not exist.")
        
    if not os.path.exists(osim_path):
        print(f"File {osim_path} does not exist.")
        
    if not os.path.exists(working_dir):
        print(f"Directory {working_dir} does not exist.")
        
    if not os.path.exists(output_path):
        print(f"Directory {output_path} does not exist.")
        
    if not os.path.exists(vtp_path):
        print(f"Directory {vtp_path} does not exist.")
        
    # test output path
    if working_dir.split('\\')[-1] != 'model_update':
        output_root = 'model_update'
    else: output_root = '.'

    # set output path
    output_path = os.path.join(output_root, 'tps_warping_results')
    if not os.path.exists(output_path):
        print(output_path)
        os.makedirs(output_path)

    # set path for controls
    control_path = os.path.join(output_root, 'tps_warping_results', 'control')
    if not os.path.exists(control_path):
        print(control_path)
        os.makedirs(control_path)