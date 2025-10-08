import os

# paths
root_dir = os.path.abspath('../')
mri_dir = os.path.abspath('../mri/results')
template_dir = os.path.abspath('../templates')

path_to_json = os.path.join(mri_dir, 'orientation.mrk.json')
xml_path = os.path.join(template_dir, 'markers_and_bone_markers_in_bodies.xml')
osim_path = os.path.join(template_dir, 'Catelli-V4.0_Nu.osim')
nrrd_path = os.path.join(mri_dir, 'athlete_03.nrrd') # path to the nrrd file with MRI data

scene_path = os.path.join(mri_dir, '2025-10-07-Scene.mrml')

vtp_path = os.path.join(template_dir, 'Geometry')

# templates
generic_model_with_bone_landmarks = os.path.join(template_dir, 'Catelli-V4.0_Nu_with_bone_skin_markers.osim')
generic_model = os.path.join(template_dir, 'Catelli-V4.0_Nu.osim')
scaling_settings_path = os.path.join(template_dir, 'scaling_setting.xml')

# created objects
bone_markers_in_ground_csv = os.path.join(template_dir, 'bone_markers_in_ground.csv')
point_order_csv = os.path.join(template_dir, 'point_order.csv')

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

# 4_update_generic_model_with_mri_data.ipynb
new_model_name = f'tps_transformed.osim'
scaled_model = os.path.join(path_to_model, 'scaled_model_joints.osim')

tps_folder = os.path.join(root_dir, 'final_results')
personalised_model_folder = os.path.join(root_dir, 'final_results', 'personalized')
if not os.path.exists(personalised_model_folder):
    os.makedirs(personalised_model_folder)
    print(f'Created directory: {personalised_model_folder}')
    
path_to_personalized_model = os.path.join(personalised_model_folder, new_model_name)

