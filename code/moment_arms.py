import os
import opensim as osim
import paths
import numpy as np

model_path = paths.USED_MODEL


# for each coordinate in the model, get the moment arms for each muscle across the range of motion
model = osim.Model(model_path)
state = model.initSystem()
coordinates = model.getCoordinateSet()
muscles = model.getMuscles()
force_set = model.getForceSet()

for muscle in muscles:
    muscle_name = muscle.getName()
    print(f"Processing muscle: {muscle_name}")
    
    for i in range(coordinates.getSize()):
        coord = coordinates.get(i)
        coord_name = coord.getName()
        # breakpoint()
        if coord.get_locked():
            print(f"Skipping coordinate {coord_name} as it is locked.")
            continue
        else:
            values = np.linspace(coord.getRangeMin(), coord.getRangeMax(), 10)
            
        coord_moment_arms = []
        for value in values:
            coord.setValue(state, value)
            model.realizeVelocity(state)
            moment_arm = muscle.computeMomentArm(state, coord)
            coord_moment_arms.append(moment_arm)
        
        if np.any(np.abs(coord_moment_arms) > 1e-3):
            print(f"Muscle {muscle_name} has non-zero moment arms for coordinate {coord_name} across the range of motion.")
            
            # add muscle name to the group for this coordinate in ForceSet in the model
            
            breakpoint()
            
        
    
        
    