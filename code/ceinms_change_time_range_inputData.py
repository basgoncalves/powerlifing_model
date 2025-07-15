import os
import paths 
import utils

xml = utils.read_xml(paths.CEINMS_INPUT_DATA)

# change tag startStopTime
tag = xml.find('startStopTime')

tag.text = f"{paths.TIME_RANGE[0]} {paths.TIME_RANGE[1]}"

# save the modified XML
try:
    utils.save_pretty_xml(xml, paths.CEINMS_INPUT_DATA)
    print(f"Updated startStopTime in {paths.CEINMS_INPUT_DATA} to {paths.TIME_RANGE[0]} {paths.TIME_RANGE[1]}")
except Exception as e:
    print(f"Error saving CEINMS input data: {e}")


