import opensim as osim
import os
import paths

basedir = paths.SIMULATION_DIR
subject = 'Athlete_03'  # Replace with actual subject name
session = '22_07_06'  # Replace with actual session name
trial = 'sq_70'  # Replace with actual trial name
setup_path = os.path.join(basedir, subject, session, trial, 'setup_SO.xml')

tool = osim.AnalyzeTool(setup_path)
os.chdir(os.path.dirname(setup_path))
tool.run()
