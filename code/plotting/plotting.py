import os
import pandas as pd
import matplotlib.pyplot as plt

try:  # Normal package-relative import
	from .. import utils  # type: ignore
except ImportError:
	# Fallback: adjust sys.path when executed without package context
	import os, sys
	project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
	if project_root not in sys.path:
		sys.path.insert(0, project_root)
	from code import utils  # type: ignore  
    
filepath = input("Enter the path to the file: ").strip().strip('"').strip("'")

df = utils.load_any_data_file(filepath)

# plot first column not time with area underneath shaded
for col in df.columns:
    if 'time' not in col.lower():
        plt.fill_between(df.index, df[col], label=col, alpha=0.5)
plt.xlabel("Index")
plt.ylabel("Value")
plt.title("Shaded Area Plot")
plt.legend()
plt.show()

breakpoint()