import os
import paths 
import utils

subject = 'Katya_01'
session = 'session1'
trial_name = 'files_in_run01'

trial = paths.Trial(subject_name=subject, session_name=session, trial_name=trial_name)

xml_file = trial.inputFiles['CEINMS_INPUT_DATA'].abspath()

input_data_tree = utils.load_any_data_file(xml_file)
tag = input_data_tree.find('.//startStopTime')
tag.text = f"{trial.TIME_RANGE[0]} {trial.TIME_RANGE[1]}"

# save the modified XML
try:
    utils.save_pretty_xml(input_data_tree, xml_file)
    print(f"Updated startStopTime in {xml_file} to {trial.TIME_RANGE[0]} {trial.TIME_RANGE[1]}")
except Exception as e:
    print(f"Error saving CEINMS input data: {e}")


