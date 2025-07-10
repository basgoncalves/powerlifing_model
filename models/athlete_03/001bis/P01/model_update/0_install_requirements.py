import subprocess
import sys

# List of required packages for 1_morph_bones_from_MRI.py
required_packages = [
    "numpy",
    "scipy",
    "nibabel",
    "matplotlib",
    "pandas"
]

def install_packages(packages):
    for package in packages:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

if __name__ == "__main__":
    install_packages(required_packages)
    print("All required packages have been installed.")