import os
import utils
import paths


if __name__ == "__main__":
    os.chdir(os.path.dirname(__file__))
    xml = utils.read_xml('.\setup.xml')
