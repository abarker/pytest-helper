#!/usr/bin/env python
"""

This module is part of a package, and also contains its own tests.

"""

from __future__ import print_function, division, absolute_import
import os
import inspect
import pytest_helper
# Init in general needed because of testing chdir call inserted below.
# The set_package option is needed because an explicit relative import is done
# before the call to script_run (even though it isn't recommended).
pytest_helper.init()

# This line is all this module really does; obviously a real, non-test module
# would do more.
test_string = "in_same_dir"

##
## Run tests.
##

from pytest_helper import PytestHelperException, LocalsToGlobalsError

# Below commented-out line FAILS and even set_package can't help it, because
# set_package imports the module under its full package name, which pytest then
# tries to also import, but it refuses to reload it and gives an "import file
# mismatch" error.  So don't do this, put script_run near top or use absolute
# imports.
#from . import dummy_module

import os
old_cwd = os.getcwd()
os.chdir("..") # Causes an error if pytest_helper.init() is not called above.

pytest_helper.script_run(self_test=True, pytest_args="-v -s")

# Put below two lines after script_run (won't be run twice).
pytest_helper.sys_path(["../package_dir"])
pytest_helper.autoimport()

os.chdir(old_cwd) # Return to prev dir so as not to mess up later tests.

# This DOES work, because pytest invocation runs it (works even with the
# self_test option passing it a filename rather than a package name).
from . import dummy_module

@fixture
def basic_setup():
    teststr = "tree"
    teststr2 = "rock"
    # Normally you'd only call locals_to_globals at the end of setup funs, like here.
    locals_to_globals()

def test_basic_stuff(basic_setup):
    assert test_string == "in_same_dir" # This is set as a global in in_sibling_dir.
    assert teststr == "tree" # Set in the fixture basic_setup and copied to globals.
    global teststr2 # Needed because teststr2 is modified below after it is used.
    assert teststr2 == "rock" # Set in the fixture basic_setup and copied to globals.
    teststr2 = "granite" # Redefine teststr2 temporarily; basic_setup will overwrite.
    assert teststr2 == "granite" # New def holds until next locals_to_globals call.

def test_autoimports(basic_setup):
    assert teststr2 == "rock" # New def above has returned to the basic_setup's def.
    teststr = "water"
    # Note that the local variable/parameter basic_setup would try to overwrite
    # the global (and fail) if locals_to_globals did not ignore parameters.
    locals_to_globals()

