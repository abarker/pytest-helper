#!/usr/bin/env python
from __future__ import print_function, division, absolute_import
import os
import inspect
import pytest_helper

# This line is all this module really does; obviously a real, non-test module
# would do more.
test_string = "in_same_dir"

##
## Run tests.
##

# Everything below can optionally be placed in an "if __name__ == '__main__'"
# conditional.  The call to script_run can optionally be placed near the top
# of the file, to avoid running the module initialization twice (for modules
# where that really matters).

# Use both relative and absolute pathnames in specifying the test file paths.
# Also include the full directory in the list to check that that works.
pytest_helper.script_run("test_in_same_dir.py", pytest_args="-v")

