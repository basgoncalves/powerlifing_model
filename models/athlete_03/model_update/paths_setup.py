import os

# paths
root_dir = os.path.abspath('../')

mri_dir = os.path.abspath('../mri/results')
path_to_json = os.path.join(mri_dir, 'orientation.mrk.json')

xml_path = os.path.join(root_dir,"templates/markers_and_bone_markers_in_bodies.xml")
osim_path = os.path.join(root_dir,'templates/Catelli-V4.0.osim')

working_dir = os.getcwd()
vtp_path = os.path.join(working_dir, 'Geometry')

# set path for controls
control_path = os.path.join(root_dir, 'mri', 'control')
if not os.path.exists(control_path):
    print(control_path)
    os.makedirs(control_path)
    
output_path = os.path.join(root_dir, 'final_results')
if not os.path.exists(output_path):
    print(output_path)
    os.makedirs(output_path)