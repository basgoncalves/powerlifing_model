import os
import sys
import time
import totalsegmentator
# cd powerlifing_model\models\athlete_03\mri\results
# TotalSegmentator -i mri.nii.gz -o segmentations --task total_mr


start_time = time.time()
print('Starting the model update process...')
time.sleep(1)

input_file = input('Enter the path to the input .nrdd file): ').strip().strip('"')
if not os.path.isfile(input_file):
    print(f'Error: The file {input_file} does not exist.')
    sys.exit(1)

input_dir = os.path.dirname(input_file)
input_filename = os.path.basename(input_file)
output_file = os.path.join(input_dir, f"{os.path.splitext(input_filename)[0]}_segmented")

try:
    breakpoint()
    totalsegmentator.python_api(input_file, output_file)
    print('\nSegmentation completed successfully!')
    print(f'Output saved in folder: {output_file}')
except Exception as e:
    print(f'An error occurred during segmentation: {e}')
    sys.exit(1)

print('Completed the model update process!')
print(f'time: {time.time() - start_time:.2f} seconds')