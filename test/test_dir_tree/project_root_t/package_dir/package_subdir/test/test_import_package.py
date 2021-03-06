#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

Doesn't test much as of now, just CWD change after init() call doesn't
break things.

"""

from __future__ import print_function, division, absolute_import
import pytest_helper
from pytest_helper import PytestHelperException, LocalsToGlobalsError
pytest_helper.init()

import os
old_cwd = os.getcwd()
os.chdir("..") # Causes an error if init() is not called above.

pytest_helper.script_run(self_test=True, pytest_args="-v -s")
# More efficient to put below two lines after script_run (won't run twice).
pytest_helper.sys_path("../../../") # contains package_dir, to import it
pytest_helper.autoimport()

os.chdir(old_cwd) # Return to prev dir so as not to mess up later tests.

# Test the pytest_helper routine get_calling_module_info
#from define_check_calling import check_calling_get_module_info
#assert check_calling_get_module_info(level=2) == "test_import_package"

def test_basic_stuff():
    # This string is set in the package's __init__ two dirs up.
    # assert package_dir.test_string == "package_init"
    var = 5
    locals_to_globals(clear=True)

def test_look_at_global():
    assert var == 5


