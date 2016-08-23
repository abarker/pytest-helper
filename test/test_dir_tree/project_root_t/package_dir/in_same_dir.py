#!/usr/bin/env python
"""

This module is tested by a test file in the same directory, inside the package.

The `script_run` call is near the bottom of the file, even though that is
not recommended, to test for and try to avoid potential problems.

"""

from __future__ import print_function, division, absolute_import
import os
import inspect
import pytest_helper
pytest_helper.init(set_package=True)

# This import *needs* the init with the set_package above in order to work.
# Would be needed, though, with script_run run from top of file instead of
# the bottom.
from . import dummy_module

# This line is all this module really does; obviously a real, non-test module
# would do more.
test_string = "in_same_dir"

##
## Run tests.
##

# Below imports both work, but commented out to not confound tests.
#import package_dir.test_in_same_dir
#from . import test_in_same_dir

pytest_helper.script_run("test_in_same_dir", pytest_args="-v", exit=False)
pytest_helper.script_run("test_in_same_dir.py", pytest_args="-v", exit=False)

# This sys.path call is needed to find the package root.
pytest_helper.sys_path("..")
pytest_helper.script_run("package_dir.test_in_same_dir", pytest_args="-v", pyargs=True)

