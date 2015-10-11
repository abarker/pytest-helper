#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
import pytest_helper

"""
This is just here to test multiple files being specified.  It doesn't do
any tests that test_in_child_dir doesn't do (and it does fewer).
"""

#import py.test
#from py.test import raises, fail, fixture, skip # fail fun can take message string arg

pytest_helper.script_run(self_test=True)
pytest_helper.sys_path(add_parent=True)
pytest_helper.auto_import()

# if __name__ == "__main__":
#     # When this file is run as a script call py.test on it.
#     """
#     import subprocess, sys
#     subprocess.call([sys.executable, "-m", "pytest", "-v", __file__])
#     #subprocess.call(["py.test-2.7", "-v", __file__])
#     sys.exit(0)
#     """
#     import sys, os, py.test
#     filePath = os.path.dirname(os.path.abspath(__file__))
#     py.test.main(["-v", __file__])
#     sys.exit(0)

from in_child_dir import *

def test_basic_stuff():
    assert test_string == "in_child_dir"

def test_autoimports():
    teststr = "water"
    with pytest.raises(KeyError):
        raise KeyError
    locals_to_globals()
    skip()
