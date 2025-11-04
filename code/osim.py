import opensim as osim
import utils
import settings


def scaleModel(modelPath): # NOT FINISHED YET
    """
    Scale the OpenSim model to match the subject's anthropometry.
    """
    model = osim.Model(modelPath)
    
    model.setName(model.getName() + "_scaled")
    
    model.printToXML(modelPath.replace('.osim', '_scaled.osim'))
    
    return model
    
def validate_markers_used(ikTool,markers_path):
    task_set = ikTool.get_IKTaskSet()
    markers = utils.load_trc(markers_path)
    markers_list = markers.columns.get_level_values(0).unique().tolist()

    for task in task_set:
        if task.getName() in markers_list:
            task.setApply(True)
            task.setWeight(task.getWeight())
        else:
            task.setApply(False)
        print(f"Task: {task.getName()}, Apply: {task.getApply()}, Weight: {task.getWeight()}")
    
    return ikTool

def scale_body_masses(modelPath):
    """ 
    Scale the body masses of model_target to match the percentages of model_reference.
    """

    model_ref = osim.Model(modelPath)

    model_targ_path = modelPath.replace('.osim', '_scaledMasses.osim')
    model_targ = osim.Model(model_targ_path)

    state1 = model_ref.initSystem()
    state2 = model_targ.initSystem()

    # prnt model weight
    print(f"Model: {model_ref.getName()}, Weight: {model_ref.getTotalMass(state1)} kg")
    print(f"Model: {model_targ.getName()}, Weight: {model_targ.getTotalMass(state2)} kg")

    # Compare each body's mass between model1 and model2
    bodyset_ref = {body.getName(): body for body in model_ref.getBodySet()}
    bodyset_targ = {body.getName(): body for body in model_targ.getBodySet()}

    print("\nComparison of body masses between model1 and model2:")

    for body_name in bodyset_ref:
        if body_name in bodyset_targ:
            mass_ref = bodyset_ref[body_name].getMass()
            mass_targ = bodyset_targ[body_name].getMass()
            percent_mass_ref = (mass_ref / model_ref.getTotalMass(state1)) * 100
            percent_mass_targ = (mass_targ / model_targ.getTotalMass(state2)) * 100
            print(f"Body: {body_name}, Model1 Mass: {mass_ref} kg ({percent_mass_ref:.2f}%), Model2 Mass: {mass_targ} kg ({percent_mass_targ:.2f}%)")
            
            # change mass of body in model2 to match model1 percentage
            if percent_mass_ref != percent_mass_targ:
                new_body_mass_targ = (percent_mass_ref / 100) * model_targ.getTotalMass(state2)
                bodyset_targ[body_name].setMass(new_body_mass_targ)
                print(f"Updated Model2 {body_name} mass to: {new_body_mass_targ} kg, {percent_mass_ref:.2f}%")
            
        else:
            mass_ref = bodyset_ref[body_name].getMass()
            print(f"Body: {body_name}, Model1 Mass: {mass_ref} kg, Model2 Mass: Not Found")
            
    # save model2 with updated masses
    model_targ.setName(model_targ.getName() + "_updated_masses")
    model_targ.printToXML(model_targ_path)
    print(f"\nUpdated model saved to: {model_targ_path}")

        
    return model_targ

def add_mass_to_body(modelPath, body_name, mass_to_add):
    """
    Add a specific mass to a body in the OpenSim model.
    """
    model = osim.Model(modelPath)
    state = model.initSystem()

    save_path = modelPath.replace('.osim', '_updatedMasses.osim')

    body = model.getBodySet().get(body_name)
    
    if body:
        current_mass = body.getMass()
        new_mass = current_mass + mass_to_add
        body.setMass(new_mass)
        model.printToXML(save_path)
        print(f"Updated {body_name} mass from {current_mass} kg to {new_mass} kg.")
    else:
        print(f"Body '{body_name}' not found in the model.")

def print_body_mass_per_segment(modelPath):
    """
    Print the mass of each body segment in the OpenSim model.
    """
    model = osim.Model(modelPath)
    state = model.initSystem()

    print("Body Segment Masses:")
    for body in model.getBodySet():
        print(f"{body.getName()}: {body.getMass()} kg ({body.getMass() / model.getTotalMass(state) * 100:.2f}%)")

def increase_isometric_force(modelPath=None, muscleList='all', factor=3):
    """
    Increase the isometric force of a specified muscle by a given factor.
    """
    if not modelPath:
        modelPath = input("Enter path to OpenSim model (.osim): ").strip('"')
    
    model = osim.Model(modelPath)
    
    if muscleList == 'all':
        muscleList = []
        for muscle in model.getMuscles():
            muscleList.append(muscle.getName())
    
    for muscle_name in muscleList:
        muscle = model.getMuscles().get(muscle_name)
        if muscle:
            current_f0 = muscle.getMaxIsometricForce()
            new_f0 = current_f0 * factor
            muscle.setMaxIsometricForce(new_f0)
            print(f"Updated {muscle_name} max isometric force from {current_f0} N to {new_f0} N.")
        else:
            print(f"Muscle '{muscle_name}' not found in the model.")

    model.printToXML(modelPath.replace('.osim', f'_increasedForce{factor}.osim'))

def create_grf_xml(markerTrcPath=None, grfMotFile=None, grfXmlPath=None):
    """
    Create a Ground Reaction Forces (GRF) XML file from marker TRC data.
    """
    if not markerTrcPath:
        markerTrcPath = input("Enter path to marker TRC file: ").strip('"')
    if not grfXmlPath:
        grfXmlPath = input("Enter path to save GRF XML file: ").strip('"')
    
    utils.generate_grf_xml_from_trc(markerTrcPath, grfXmlPath)
    print(f"GRF XML file created at: {grfXmlPath}")
    

if __name__ == "__main__":
    
    LocalFuncs = [f for f in dir() if callable(globals()[f])]
    print("Available commands:", LocalFuncs)

    # Command loop
    while True:
        command = input("Enter command: ")

        if not command in LocalFuncs:
            print("Invalid command. Please try again.")
            continue

        try:
            globals()[command]()
        except Exception as e:
            print(f"Error executing {command}: {e}")

        print("Command executed successfully.")