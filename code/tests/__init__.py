"""Test package initializer.

Provides access to `utils` whether tests are run via
  python -m code.tests.some_test_module
or a direct path / discovery tool that doesn't set the parent package.
"""

try:  # Normal package-relative import
	from .. import utils  # type: ignore
except ImportError:
	# Fallback: adjust sys.path when executed without package context
	import os, sys
	project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
	if project_root not in sys.path:
		sys.path.insert(0, project_root)
	from code import utils  # type: ignore  # noqa: E401

