import opensim as osim
import os
import paths

basedir = paths.SIMULATION_DIR
# Replace with actual subject name, session name, and trial name
subject = 'Athlete_03'
session = '22_07_06'
trial = 'sq_70'
setup_path = os.path.join(basedir, subject, session, trial, 'setup_SO.xml')

#change to tool depending what you want to analyze (e.g. tool = osim.InverseKinematicsTool(setup_path), tool = osim.ForwardDynamicsTool(setup_path))
tool = osim.AnalyzeTool(setup_path) 

os.chdir(os.path.dirname(setup_path))
tool.run()
