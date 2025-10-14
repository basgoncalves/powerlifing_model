import os
import xml.etree.ElementTree as ET
import vtk

class VTP:
    def __init__(self, input_file_path, output_file_path):
        self.input_file_path = input_file_path
        self.output_file_path = output_file_path

    def read(self, input_file_path=None):
        """Read and return the VTP file using VTK."""

        if input_file_path.endswith('.vtp'):
            reader = vtk.vtkXMLPolyDataReader()

        elif input_file_path.endswith('.obj'):
            reader = vtk.vtkOBJReader()

        elif input_file_path.endswith('.stl'):
            reader = vtk.vtkSTLReader()

        reader.SetFileName(input_file_path)
        reader.Update()

        return reader

    def plot(self):
        """Visualize the VTP file using VTK."""

        # Read the VTP file
        reader = self.read(self.input_file_path)

        # Get the output polydata
        polydata = reader.GetOutput()

        # Create a mapper and actor
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(polydata)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        # Create a renderer, render window, and interactor
        renderer = vtk.vtkRenderer()
        renderer.AddActor(actor)
        renderer.SetBackground(0.1, 0.2, 0.4)  # Dark blue background

        render_window = vtk.vtkRenderWindow()
        render_window.AddRenderer(renderer)

        interactor = vtk.vtkRenderWindowInteractor()
        interactor.SetRenderWindow(render_window)

        # Set window name before rendering
        render_window.SetWindowName("VTP Viewer")

        # Start the visualization
        render_window.Render()
        interactor.Start()


    def mirror_vtp_xml(self):
        """Mirror a VTP file by negating X coordinates using XML parsing."""

        # Parse the XML file
        tree = ET.parse(self.input_file_path)
        root = tree.getroot()

        # Find Normals DataArray
        normals = root.find(".//PointData/DataArray[@Name='Normals']")
        if normals is not None:
            normal_values = normals.text.strip().split()
            # Negate every 3rd value starting from index 0 (X component)
            mirrored_normals = []
            for i in range(0, len(normal_values), 3):
                x = float(normal_values[i]) * -1
                y = float(normal_values[i+1])
                z = float(normal_values[i+2])
                mirrored_normals.extend([x, y, z])

            # Format back to text with same structure (3 values per line)
            formatted_normals = []
            for i in range(0, len(mirrored_normals), 3):
                formatted_normals.append(f"{mirrored_normals[i]:.6f} {mirrored_normals[i+1]:.6f} {mirrored_normals[i+2]:.6f}")
            normals.text = "\n\t\t\t" + "\n\t\t\t".join(formatted_normals) + "\n\t\t"

        # Find Points DataArray
        points = root.find(".//Points/DataArray[@Name='Points']")
        if points is not None:
            point_values = points.text.strip().split()
            # Negate every 3rd value starting from index 0 (X coordinate)
            mirrored_points = []
            for i in range(0, len(point_values), 3):
                x = float(point_values[i]) * -1
                y = float(point_values[i+1])
                z = float(point_values[i+2]) * -1
                mirrored_points.extend([x, y, z])

            # Format back to text with same structure
            formatted_points = []
            for i in range(0, len(mirrored_points), 3):
                formatted_points.append(f"{mirrored_points[i]:.6f} {mirrored_points[i+1]:.6f} {mirrored_points[i+2]:.6f}")
            points.text = "\n\t\t\t" + "\n\t\t\t".join(formatted_points) + "\n\t\t"

        # Write to output file
        tree.write(self.output_file_path, encoding='utf-8', xml_declaration=True)
        print(f"Mirrored geometry saved to {self.output_file_path}")

    def convert_obj_to_vtp(self):
        """Convert an OBJ file to VTP format using VTK."""

        if not self.input_file_path.lower().endswith('.obj'):
            print("Input file must be an OBJ file.")
            return

        # Read the OBJ file
        reader = vtk.vtkOBJReader()
        reader.SetFileName(self.input_file_path)
        reader.Update()

        # Get the output polydata
        polydata = reader.GetOutput()

        # Write to VTP file
        writer = vtk.vtkXMLPolyDataWriter()
        writer.SetFileName(self.output_file_path)
        writer.SetInputData(polydata)
        writer.Write()
        print(f"Converted {self.input_file_path} to {self.output_file_path}")

    def convert_obj_to_stl(self):
        """Convert an OBJ file to STL format using VTK."""


        if not self.input_file_path.lower().endswith('.obj'):
            print("Input file must be an OBJ file.")
            return

        if not self.output_file_path.lower().endswith('.stl'):
            print("Output file must be an STL file.")
            return

        # Read the OBJ file
        reader = vtk.vtkOBJReader()
        reader.SetFileName(self.input_file_path)
        reader.Update()

        # Get the output polydata
        polydata = reader.GetOutput()

        # Write to STL file
        stl_writer = vtk.vtkSTLWriter()
        stl_writer.SetFileName(self.output_file_path)
        stl_writer.SetInputData(polydata)
        stl_writer.Write()
        print(f"output saved: {self.output_file_path}")

    def resize(self, scale_factor):
        """Resize the geometry by a given scale factor."""

        # Read the VTP file
        reader = self.read(self.input_file_path)

        # Get the output polydata
        polydata = reader.GetOutput()

        # Apply scaling
        transform = vtk.vtkTransform()
        transform.Scale(scale_factor, scale_factor, scale_factor)

        transform_filter = vtk.vtkTransformPolyDataFilter()
        transform_filter.SetInputData(polydata)
        transform_filter.SetTransform(transform)
        transform_filter.Update()

        # Determine output file type and use appropriate writer
        output_extension = self.output_file_path.lower().split('.')[-1]

        if output_extension == 'stl':
            writer = vtk.vtkSTLWriter()
        elif output_extension == 'vtp':
            writer = vtk.vtkXMLPolyDataWriter()
        else:
            print(f"Unsupported output format: {output_extension}")
            return

        writer.SetFileName(self.output_file_path)
        writer.SetInputData(transform_filter.GetOutput())
        writer.Write()
        print(f"Resized geometry saved to {self.output_file_path}")

    def measure_dimensions(self):
        """Measure and return the dimensions of the geometry."""

        # Read the VTP file
        reader = self.read(self.input_file_path)

        # Get the output polydata
        polydata = reader.GetOutput()

        # Get bounds
        bounds = polydata.GetBounds()  # (xmin, xmax, ymin, ymax, zmin, zmax)
        dimensions = (bounds[1] - bounds[0], bounds[3] - bounds[2], bounds[5] - bounds[4])

        return dimensions



def mirror_vtp_xml(geomDir, fileDict=None):
    """Mirror a VTP file by negating X coordinates using XML parsing."""

    if fileDict is None:
        fileDict = {}

        for name in os.listdir(geomDir):
            if name.endswith('.vtp') and not name.endswith('_mirror.vtp'):
                fileDict[name.replace('.vtp', '')] = name.replace('.vtp', '_mirror.vtp')

    for name, mirrored_file in fileDict.items():
        vtp = VTP(input_file_path=f"{geomDir}/{name}.vtp",
                  output_file_path=f"{geomDir}/{mirrored_file}.vtp")
        vtp.mirror_vtp_xml()


if __name__ == "__main__":



    # Mirror the VTP files from the dictionary
    if False:
        geomDir = r"C:\Users\Bas\Documents\OpenSim\4.5\Models\UpperBody"

        fileDict = {"scapula": "scapula_mirror",
            "humerus": "humerus_mirror",
            "ulna": "ulna_mirror",
            "radius": "radius_mirror"}


        mirror_vtp_xml(geomDir, fileDict)

    # Convert an OBJ file to VTP format
    if True:
        objectPath = input("Enter the path to the .obj file: ").strip().strip('"')
        vtp = VTP( input_file_path=objectPath,
                    output_file_path=objectPath.replace('.obj', '.stl'))

        vtp.convert_obj_to_stl()
        vtp.input_file_path = vtp.output_file_path
        vtp.resize(scale_factor=0.01)

        # vtp.plot()
        dimensions = vtp.measure_dimensions()
        print(f"Dimensions (X, Y, Z): {dimensions}")
        



