import opensim, os, sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
    
from .. import paths

def print_muscles(model_path):
    model = opensim.Model(model_path)
    muscle_set = model.getMuscles()
    print(f"Muscles in model '{model_path}':")
    for i in range(muscle_set.getSize()):
        muscle = muscle_set.get(i)
        print(f"- {muscle.getName()}")

if __name__ == "__main__":
    # Replace with your .osim model file path
    subject = 'Athlete_03'
    session = 'Session_01'
    trial_name = 'Trial_01'
    trial = paths.Trial(subject_name=subject, session_name=session, trial_name=trial_name)
    
    print_muscles(trial.USED_MODEL)