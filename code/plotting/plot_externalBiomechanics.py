import os
import numpy as np
import pandas as pd
from pathlib import Path

SIMULATIONS_DIR = r'C:\Git\1_current_projects\Fatigue-prediction-MSC-Thesis\data\simulations'
SUBJECT_LIST = os.listdir(SIMULATIONS_DIR)
SESSION = 'pre'

class Trial:
	def __init__(self, path, ikOutput, idOutput):
		self.path = path
		self.ikOutput = ikOutput
		self.idOutput = idOutput
		self.name = Path(path).name
		self.session = Path(path).parent.name
		self.subject = Path(path).parent.parent.name

class Analysis:
	def __init__(self, ikFileName = '_ik.mot', idFileName = '_id.sto'):
		self.trialList = []
		self.ikColumns = ['hip_flexion_r', 'hip_flexion_l', 
                        		'knee_angle_r', 'knee_angle_l', 
                          		'ankle_angle_r', 'ankle_angle_l']
		
		# walk through all subjects and find all unique files
		for subject in SUBJECT_LIST:
			subject_path = os.path.join(SIMULATIONS_DIR, subject)
			sessions = os.listdir(subject_path)
			for session in sessions:
				if session != SESSION:
					continue
				session_path = os.path.join(subject_path, session)
				trials = os.listdir(session_path)
				for trial in trials:
					trial_path = os.path.join(session_path, trial)
					ikOutput = trial_path + '\\' + ikFileName
					idOutput = trial_path + '\\' + idFileName
					if os.path.exists(ikOutput) and os.path.exists(idOutput):
						self.addTrial(Trial(trial_path, ikOutput, idOutput))
      
	def addTrial(self, trial: Trial):
		self.trialList.append(trial)

if __name__ == "__main__":
	ikFileName = 'ik.mot'
	idFileName = 'id.sto'
	analysis = Analysis(ikFileName, idFileName)
 
	breakpoint()
