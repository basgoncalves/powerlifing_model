import os

# paths
root_dir = os.path.abspath('../')

mri_dir = os.path.abspath('../mri/results')
path_to_json = os.path.join(mri_dir, 'orientation.mrk.json')

xml_path = os.path.join(root_dir,"templates/markers_and_bone_markers_in_bodies.xml")
osim_path = os.path.join(root_dir,'templates/Catelli-V4.0.osim')

working_dir = os.getcwd()
vtp_path = os.path.join(working_dir, 'Geometry')

# create these if do not exist
control_path = os.path.join(root_dir, 'mri', 'control')
if not os.path.exists(control_path):
    os.makedirs(control_path)
    print(f'Created directory: {control_path}')
    
output_path = os.path.join(root_dir, 'final_results')
if not os.path.exists(output_path):
    os.makedirs(output_path)
    print(f'Created directory: {output_path}')
    
# IMPORTANT : THESE SHOULD BE PERSON-SPECIFIC
mass_text = '94.5'
height_text = '1.60'
age_text = '33'

# path to experimental .trc file : <marker_file>
experimental_markers = os.path.join(root_dir, 'motion_lab/static/static_01/task.trc')

# paths to generic model and marker set
path_to_generic_model = os.path.join(root_dir, 'templates/Catelli-V4.0.osim')
path_to_generic_marker_set =  os.path.join(root_dir, 'templates/generic_skin_markers.xml')


# <output_scale_file>
path_to_model = os.path.join(root_dir, 'final_results', 'generic_scaled')
if not os.path.exists(path_to_model):
    print(path_to_model)
    os.makedirs(path_to_model)

output_scale_file = os.path.join(path_to_model, 'output_scale_file.txt')
output_model_file = os.path.join(path_to_model, f'scaled_model.osim')  
output_scaling_settings = os.path.join(path_to_model, f'scaling_setting.xml')
