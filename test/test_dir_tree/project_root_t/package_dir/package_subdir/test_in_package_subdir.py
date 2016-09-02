#!/usr/bin/env python
from __future__ import print_function, division, absolute_import
import os
import inspect
import pytest_helper
import set_package_attribute

if __name__ == "__main__":
    #pytest_helper.init(set_package=True) # Finds no tests when this is set!
    pytest_helper.init()
    import sys
    #pytest_helper.script_run(self_test=True)
    pytest_helper.script_run(self_test="test_in_package_subdir", pyargs=True)

pytest_helper.sys_path("../../..")
from package_dir.package_subdir import subdir_dummy_module

pytest_helper.autoimport()
def test_running_test_in_package_subdir():
    assert True

