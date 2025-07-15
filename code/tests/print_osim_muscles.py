import opensim
import paths

def print_muscles(model_path):
    model = opensim.Model(model_path)
    muscle_set = model.getMuscles()
    print(f"Muscles in model '{model_path}':")
    for i in range(muscle_set.getSize()):
        muscle = muscle_set.get(i)
        print(f"- {muscle.getName()}")

if __name__ == "__main__":
    # Replace with your .osim model file path
    model_file = paths.USED_MODEL
    print_muscles(model_file)