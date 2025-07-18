import opensim as osim
import paths
import scipy.io

# matfile = r"C:\Git\1_current_projects\powerlifing_model\willi_data\Athlete_03\sq_70\settings.mat"
# # open matfile

# mat_data = scipy.io.loadmat(matfile)
# mat_data['model_mass']
# print(f"Model mass from mat file: {mat_data['model_mass'][0][0]} kg")
# exit()

# model = osim.Model(paths.USED_MODEL)
def scale_body_masses(model_reference_path, model_target_path,save_path=None):
    """
    Scale the body masses of model_target to match the percentages of model_reference.
    """

    model_ref = osim.Model(model_reference_path)
    model_targ = osim.Model(model_target_path)

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
    if save_path is not None:
        model_targ.printToXML(save_path)
        print(f"\nUpdated model saved to: {model_target_path.replace('.osim', '_updated_masses.osim')}")
    else:
        print(f"\nUpdated NOT SAVED")
        
    return model_targ
    
def add_mass_to_body(model_path, body_name, mass_to_add, save_path):
    """
    Add a specific mass to a body in the OpenSim model.
    """
    model = osim.Model(model_path)
    state = model.initSystem()

    body = model.getBodySet().get(body_name)
    if body:
        current_mass = body.getMass()
        new_mass = current_mass + mass_to_add
        body.setMass(new_mass)
        model.printToXML(save_path)
        print(f"Updated {body_name} mass from {current_mass} kg to {new_mass} kg.")
    else:
        print(f"Body '{body_name}' not found in the model.")

def print_body_mass_per_segment(model_path):
    """
    Print the mass of each body segment in the OpenSim model.
    """
    model = osim.Model(model_path)
    state = model.initSystem()

    print("Body Segment Masses:")
    for body in model.getBodySet():
        print(f"{body.getName()}: {body.getMass()} kg ({body.getMass() / model.getTotalMass(state) * 100:.2f}%)")

if __name__ == "__main__":
    
    
    model_reference_path = r"C:\OpenSim 4.5\Models\Rajagopal\generic_unscaled.osim"
    model_target_path = paths.Analysis().SUBJECTS[0].SESSIONS[0].TRIALS[0].USED_MODEL
    print(f"Reference model path: {model_reference_path}")
    print(f"Target model path: {model_target_path}")
    
    # print model masses
    model_ref = osim.Model(model_reference_path)
    model_targ = osim.Model(model_target_path)
    state1 = model_ref.initSystem()
    state2 = model_targ.initSystem()
    print(f"Model: {model_reference_path}, Weight: {model_ref.getTotalMass(state1)} kg")
    print(f"Model: {model_target_path}, Weight: {model_targ.getTotalMass(state2)} kg")

    print_body_mass_per_segment(model_target_path)

    exit()
    
    scale_body_masses(model_reference_path=model_reference_path,
                      model_target_path=model_target_path,
                      save_path=model_target_path.replace('.osim', '_scaledMasses.osim')
                      )
    print("Body masses scaled and model saved successfully.")
    
    add_mass_to_body(model_path=model_target_path.replace('.osim', '_scaledMasses.osim'),
                     body_name='pelvis',
                     mass_to_add=220,
                     save_path = model_target_path.replace('.osim', '_scaledMasses.osim'))
    
    print("Added 220 kg to pelvis body and saved model successfully.")