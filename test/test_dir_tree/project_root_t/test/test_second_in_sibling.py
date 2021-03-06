#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
import pytest_helper

"""
This is just here to test multiple files being specified.  It doesn't do
any tests that test_in_child_dir doesn't do (and it does fewer).
"""

pytest_helper.script_run(self_test=True)
pytest_helper.sys_path("../package_dir")
pytest_helper.autoimport()

from in_sibling_dir import *

def test_basic_stuff():
    assert test_string == "in_sibling_dir"

def test_autoimports():
    teststr = "water"
    with pytest.raises(KeyError):
        raise KeyError
    locals_to_globals()
