#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
import pytest_helper
from pytest_helper import PytestHelperException, LocalsToGlobalsError

# TODO see the in_same_dir file for details!!!

# TODO script_fun FAILS if the below is used!!!!!!!!
#if __name__ == "__main__":
#    import set_package_attribute
#    set_package_attribute.init()
print("in test_in_same_dir, the __package__ attribute is", __package__)
#pytest_helper.sys_path("..")
#from .in_same_dir import * # fails *without* above, but script_run fails with it
#from package_dir.in_same_dir import * # still works in both cases if .. in path

pytest_helper.init() # Needed because of testing chdir call inserted below.

import os
old_cwd = os.getcwd()
os.chdir("..") # Causes an error if pytest_helper.init() is not called above.

#pytest_helper.script_run(self_test=True, pytest_args="-v -s")
print("calling script_run in test file")
pytest_helper.script_run("package_dir.test_in_same_dir", pytest_args="-v -s --pyargs")
print("made it past script_run call in test file")

# More efficient to put below two lines after script_run (won't run twice).
pytest_helper.auto_import()
pytest_helper.sys_path(add_self=True) # Needs to add own dir when run as test.

# The module to be tested is in_same_dir.
# The import below defines test_string="in_same_dir".
from .in_same_dir import *  # Needs the dot or fails when run from in_same_dir.py

# Test restoring the system path.
pytest_helper.sys_path("../package_dir/test")
pytest_helper.restore_previous_sys_path()
with raises(ImportError):
    import test_in_child_dir # This succeeds without the restore above.
    
os.chdir(old_cwd) # Return to prev dir so as not to mess up later tests.

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

def test_skip():
    skip()

