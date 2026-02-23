import os
import opensim as osim
import xml.etree.ElementTree as ET
from copy import deepcopy


def add_wrapping_surfaces(reference_model_path, target_model_path, output_model_path):
    """
    Add wrapping surfaces from reference OpenSim model to target model in two stages:
    1. Use OpenSim API to add wrap objects to bodies
    2. Use XML parsing to copy PathWrapSet elements for matching muscles
    
    Args:
        reference_model_path (str): Path to reference .osim file
        target_model_path (str): Path to target .osim file
        output_model_path (str): Path for output .osim file with wrapping surfaces
    """
    try:
        print("=" * 60)
        print("STAGE 1: Adding wrapping surfaces using OpenSim API")
        print("=" * 60)
        
        # Load both models
        reference_model = osim.Model(reference_model_path)
        target_model = osim.Model(target_model_path)
        reference_model.initSystem()
        target_model.initSystem()
        
        # Get wrapping surfaces from reference model
        reference_bodies = reference_model.getBodySet()
        target_bodies = target_model.getBodySet()
        
        # Add wrapping surfaces to target model using API
        wrapping_surfaces_added = 0
        for i in range(reference_bodies.getSize()):
            ref_body = reference_bodies.get(i)
            wrapping_surfaces = ref_body.getWrapObjectSet()
            
            if wrapping_surfaces.getSize() > 0:
                try:
                    target_body = target_bodies.get(ref_body.getName())
                    target_wrap_set = target_body.getWrapObjectSet()
                    
                    for j in range(wrapping_surfaces.getSize()):
                        wrap_obj = wrapping_surfaces.get(j)
                        wrap_name = wrap_obj.getName()
                        
                        # Check if surface already exists
                        if target_wrap_set.getIndex(wrap_name) >= 0:
                            print(f"  ⚠ Skipped '{wrap_name}' on '{target_body.getName()}' (already exists)")
                        else:
                            # Clone the wrap object
                            cloned_wrap = wrap_obj.clone()
                            target_body.addWrapObject(cloned_wrap)
                            print(f"  ✓ Added '{wrap_name}' to '{target_body.getName()}'")
                            wrapping_surfaces_added += 1
                except RuntimeError:
                    print(f"  ✗ Body '{ref_body.getName()}' not found in target model")
        
        # Save target model with wrapping surfaces
        target_model.printToXML(output_model_path)
        print(f"\n✓ Saved model after API changes: {output_model_path}\n")
        
        print("=" * 60)
        print("STAGE 2: Adding PathWrapSets using XML parsing")
        print("=" * 60)
        
        # Parse both XML files
        print("Parsing reference and target model XML files...")
        ref_tree = ET.parse(reference_model_path)
        ref_root = ref_tree.getroot()
        
        target_tree = ET.parse(output_model_path)
        target_root = target_tree.getroot()
        
        # Remove namespaces for easier parsing
        def remove_namespaces(root):
            for elem in root.iter():
                if '}' in elem.tag:
                    elem.tag = elem.tag.split('}', 1)[1]
        
        remove_namespaces(ref_root)
        remove_namespaces(target_root)
        print("✓ Namespaces removed\n")
        
        # Find all Millard2012EquilibriumMuscle elements
        ref_muscles = ref_root.findall('.//Millard2012EquilibriumMuscle')
        target_muscles = target_root.findall('.//Millard2012EquilibriumMuscle')
        
        print(f"Found {len(ref_muscles)} muscles in reference model")
        print(f"Found {len(target_muscles)} muscles in target model\n")
        
        path_wraps_added = 0
        muscles_with_wraps = 0
        
        # Map target muscles by name for quick lookup
        target_muscles_by_name = {m.get('name'): m for m in target_muscles if m.get('name')}
        
        # Process each reference muscle
        for ref_muscle in ref_muscles:
            ref_muscle_name = ref_muscle.get('name')
            if not ref_muscle_name:
                continue
            
            # Find corresponding target muscle
            target_muscle = target_muscles_by_name.get(ref_muscle_name)
            if target_muscle is None:
                continue
            
            # Get reference muscle's geometry path and PathWrapSet
            # Search for GeometryPath regardless of name attribute value
            ref_geometry_path = None
            for child in ref_muscle:
                if child.tag == 'GeometryPath':
                    ref_geometry_path = child
                    break
            
            if ref_geometry_path is None:
                continue
            
            ref_path_wrap_set = ref_geometry_path.find('PathWrapSet')
            if ref_path_wrap_set is None:
                continue
            
            # Get reference PathWrap objects
            ref_objects = ref_path_wrap_set.find('objects')
            ref_path_wraps = ref_objects.findall('PathWrap') if ref_objects is not None else []
            
            if len(ref_path_wraps) == 0:
                continue  # No PathWraps to copy
            
            # Get target muscle's geometry path and PathWrapSet
            target_geometry_path = None
            for child in target_muscle:
                if child.tag == 'GeometryPath':
                    target_geometry_path = child
                    break
            
            if target_geometry_path is None:
                continue
            
            target_path_wrap_set = target_geometry_path.find('PathWrapSet')
            if target_path_wrap_set is None:
                continue
            
            # Get or create objects element in target PathWrapSet
            target_objects = target_path_wrap_set.find('objects')
            if target_objects is None:
                target_objects = ET.SubElement(target_path_wrap_set, 'objects')
            else:
                # Clear existing PathWraps (remove all children)
                for child in list(target_objects):
                    target_objects.remove(child)
            
            # Ensure groups element exists
            target_groups = target_path_wrap_set.find('groups')
            if target_groups is None:
                ET.SubElement(target_path_wrap_set, 'groups')
            
            # Copy all PathWrap elements from reference to target
            for ref_path_wrap in ref_path_wraps:
                # Create a deep copy of the PathWrap element
                new_path_wrap = deepcopy(ref_path_wrap)
                target_objects.append(new_path_wrap)
                
                path_wrap_name = ref_path_wrap.get('name', 'unknown')
                wrap_obj_name = ref_path_wrap.findtext('wrap_object', 'unknown')
                print(f"  ✓ '{path_wrap_name}' → '{ref_muscle_name}' (wraps: {wrap_obj_name})")
                
                path_wraps_added += 1
            
            # Verify elements were added
            if len(list(target_objects)) > 0:
                muscles_with_wraps += 1
            else:
                print(f"  ⚠ Warning: No PathWraps actually added to '{ref_muscle_name}' objects element")
        
        # Update model name
        model_elem = target_root.find('Model')
        if model_elem is not None:
            current_name = model_elem.get('name')
            if current_name and '_with_wrapping' not in current_name:
                model_elem.set('name', current_name + '_with_wrapping')
        
        # Save the final XML
        print(f"\nWriting final model to: {output_model_path}")
        
        # Write the tree with proper XML declaration and method
        with open(output_model_path, 'wb') as f:
            target_tree.write(f, encoding='UTF-8', xml_declaration=True, method='xml')

        # open in API and save again to ensure formatting is consistent with OpenSim standards
        final_model = osim.Model(output_model_path)
        final_model.printToXML(output_model_path)
        
        print("✓ XML write completed")
        
        # Summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        print(f"Wrapping surfaces added (API):     {wrapping_surfaces_added}")
        print(f"Muscles with PathWraps (XML):      {muscles_with_wraps}")
        print(f"Total PathWraps copied:             {path_wraps_added}")
        print(f"\nOutput model: {output_model_path}")
        print(f"{'='*60}")
        
    except ImportError:
        print("Error: OpenSim Python API not installed. Please install opensim package.")
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    print("=== Add Wrapping Surfaces to OpenSim Model ===\n")
    
    reference_path = input("Enter path to reference model (.osim): ").strip('"')
    target_path = input("Enter path to target model (.osim): ").strip('"')
    output_path = target_path.replace('.osim', '_with_wrapping.osim')
    
    if os.path.exists(reference_path) and os.path.exists(target_path):
        add_wrapping_surfaces(reference_path, target_path, output_path)
    else:
        print("Error: One or both input files do not exist.")