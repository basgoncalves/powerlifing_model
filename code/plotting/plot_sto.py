"""Entry point for plotting .sto data.

Correct ways to run:
  1) As a module (recommended, enables relative imports):
	   python -m code.plotting.plot_sto
  2) Direct script path (fallback logic will adjust sys.path):
	   python code\plotting\plot_sto.py

Incorrect (will fail):
	   python -m code.plotting.plot_sto.py   # don't include .py
"""

# Preferred relative import (works when run with -m)
try:
	from .. import utils  # noqa: F401
except ImportError:
	# Fallback: adjust sys.path when executed directly (no package context)
	import os, sys  # noqa: E401
	project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
	if project_root not in sys.path:
		sys.path.insert(0, project_root)
	# Re-attempt import via package path
	from code import utils  # type: ignore # noqa: F401

def main():
	print("plot_sto main stub. utils imported:", hasattr(utils, '__file__'))
	# TODO: implement actual plotting logic here (read .sto, plot signals)

if __name__ == "__main__":
	main()
 