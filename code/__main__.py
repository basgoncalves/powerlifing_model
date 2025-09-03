print('Running code for powerlifting model...')

import opensim as osim
import utils
import main
import paths

settings = paths.Settings()
models = paths.Models(subject_name='Athlete_03')

muscleList = ['bflh_r', 'bflh_l']
osimPath = models.SCALED_MODEL
print(utils.get_muscle_params(osimModelPath=osimPath, muscleList=muscleList))

