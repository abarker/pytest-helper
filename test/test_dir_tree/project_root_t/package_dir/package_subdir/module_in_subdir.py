#!/usr/bin/env python
from __future__ import print_function, division, absolute_import
import os
import inspect
import pytest_helper
pytest_helper.init(set_package=True)

# This line is all this module really does; obviously a real, non-test module
# would do more.
test_string = "in_child_dir"

#import set_package_attribute # Test setting the package attribute for scripts.
from . import subdir_dummy_module # Works! now this doesn't give an error.
from .. import dummy_module # Works! now this doesn't give an error.

import sys
sys.exit(0) # TODO currently only testing relative imports...

##
## Run tests.
##

# Everything below can optionally be placed in an "if __name__ == '__main__'"
# conditional.  The call to script_run can optionally be placed near the top
# of the file, to avoid running the module initialization twice (for modules
# where that really matters).

# Get this file's absolute dir path to test passing absolute pathnames in calls
# to pytest_helper.
this_files_dir = os.path.dirname(os.path.abspath(inspect.getsourcefile(lambda:0)))
path_to_second_test = os.path.join(this_files_dir, "test/second_test.py")

# Use both relative and absolute pathnames in specifying the test file paths.
# Also include the full directory in the list to check that that works.
pytest_helper.script_run(testfile_paths=["test/test_in_child_dir.py",
                         path_to_second_test, "test"], pytest_args="-v")

