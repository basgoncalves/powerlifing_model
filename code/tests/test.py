import os
import time
from xml.dom import minidom
import opensim as osim
import xml.etree.ElementTree as ET


osimPath = input("osimpath:'").strip('"')

# time take to load opensim
start_time = time.time()
model = osim.Model(osimPath)
end_time = time.time()
print(f"Time taken to load OpenSim model: {end_time - start_time:.2f} seconds")

# time taken to load as xml
start_time = time.time()
tree = ET.parse(osimPath)
end_time = time.time()
print(f"Time taken to parse OpenSim model as XML: {end_time - start_time:.2f} seconds")

def save_pretty_xml(tree, save_path):
            """Saves the XML tree to a file with proper indentation and no blank lines."""
            rough_string = ET.tostring(tree.getroot(), 'utf-8')
            reparsed = minidom.parseString(rough_string)
            pretty_xml = reparsed.toprettyxml(indent="   ")
            # Remove blank lines
            pretty_xml_no_blanks = "\n".join([line for line in pretty_xml.splitlines() if line.strip()])
            with open(save_path, 'w') as file:
                file.write(pretty_xml_no_blanks)

        
start_time = time.time()
# save new xml
output_xml_path = osimPath.replace('.osim', '_copy.osim')
save_pretty_xml(tree, output_xml_path)
print(f"Copied OpenSim model XML saved to: {output_xml_path}")
print("time taken to save OpenSim model as XML:", time.time() - start_time)

# save new model
start_time = time.time()
output_model_path = osimPath.replace('.osim', '_model.osim')
model.printToXML(output_model_path)
print(f"Copied OpenSim model saved to: {output_model_path}")
print("time taken to save OpenSim model using OpenSim API:", time.time() - start_time)
