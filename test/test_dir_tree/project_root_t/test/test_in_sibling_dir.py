#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
import pytest_helper
from pytest_helper import PytestHelperException, LocalsToGlobalsError
pytest_helper.init() # Needed because testing with a chdir call, inserted below.

import os
old_cwd = os.getcwd()
os.chdir("..") # Causes an error if pytest_helper.init() is not called above.

pytest_helper.script_run(self_test=True, pytest_args="-v -s")
# More efficient to put below two lines after script_run (won't run twice).
pytest_helper.sys_path(["../package_dir"])
pytest_helper.auto_import()

# The module to be tested is in_sibling_dir.
# The import below defines test_string="in_sibling_dir".
from in_sibling_dir import *

os.chdir(old_cwd) # Return to prev dir so as not to mess up later tests.

@fixture
def basic_setup():
    teststr = "tree"
    teststr2 = "rock"
    # Normally you'd only call locals_to_globals at the end of setup funs, like here.
    locals_to_globals()

def test_basic_stuff(basic_setup):
    assert test_string == "in_sibling_dir" # This is set as a global in in_sibling_dir.
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

# Note that the below tests are testing some unusual use-patterns of
# locals_to_globals just to make sure things work as expected.  Normally you'd
# only put the call at the end of the setup functions.

def test_locals_to_globals():
    global teststr # REQUIRED only because teststr is first used, then set to a value.
    assert teststr == "water"
    new_var = "car"
    clear_locals_from_globals() # This CLEARS the global teststr, since it was copied.
    with raises(NameError):
        assert teststr == "water"

    # Below line copies only new_var, which is saved to delete later.  But teststr is
    # still global, and is set below.  Can causes problems calling locals_to_globals
    # not at the end of setup functions when some are made global and later modified.
    locals_to_globals()

    with raises(LocalsToGlobalsError):
        locals_to_globals(auto_clear=False)
    teststr = "house" # This now sets a global, which will NOT be cleared.
    locals_to_globals()
    assert teststr == "house"
   
class TestInClass(object):
    def test_in_class(self):
        # TODO DEBUG uncomment below to see nasty bug after multiple runs.
        #assert teststr == "house" # Test the previously-set global.
        locals_to_globals() # This clears previously-set globals as a side-effect.
        #assert teststr == "house" # Still defined, since it was set as global.
        with raises(NameError):
            assert new_var == "car" # No longer defined; copied on call before last.

        # Below del is NEEDED if a later test wants to copy a local of same name,
        # unless called with noclobber set to False (as currently set below).
        #del globals()["teststr"]
        #with raises(NameError):
        #    assert teststr == "house"

def test_final1():
    teststr = "water"
    locals_to_globals(noclobber=False)
    assert teststr == "water"

def test_final2():
    assert teststr == "water"
    locals_to_globals(locals(), globals())
    with raises(NameError):
        assert teststr == "water"

