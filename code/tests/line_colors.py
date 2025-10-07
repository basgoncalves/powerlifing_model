
from matplotlib import pyplot as plt


try:  # Normal package-relative import
	from .. import utils  # type: ignore
except ImportError:
	# Fallback: adjust sys.path when executed without package context
	import os, sys
	project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
	if project_root not in sys.path:
		sys.path.insert(0, project_root)
	from code import paths  # type: ignore  # noqa: E401

muscleMapping = paths.Settings().Muscle_Groups

# create a dict of line colors and line styles for when groups need to be plotted
line_styles = {'R': {'linestyle': '-'},
                'L': {'linestyle': '--'},
                'O': {'linestyle': ':'}}
# Group muscles by their base name (e.g., 'Adductors' for 'R Adductors' and 'L Adductors')
base_muscle_groups = list(set(
    key.replace('R ', '').replace('L ', '') for key in muscleMapping.keys()))
# Create a color map for the base muscle groups
colors = plt.colormaps.get_cmap('tab20')
line_colors = {group: {'color': colors(i)} for i, group in enumerate(base_muscle_groups)}
for i, group in enumerate(muscleMapping.keys()):

    muscle = group.replace('R ', '').replace('L ', '')
    muscle_list = muscleMapping[group]
    leg = group[0]
    style = line_styles[leg]['linestyle']
    color = line_colors[muscle]['color']
    muscleMapping[group] = {'muscles': muscle_list, 'color': color, 'linestyle': style}