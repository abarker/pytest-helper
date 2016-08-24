# -*- coding: utf-8 -*-
"""
Description
-----------

This file contains global variable settings and exceptions used by multiple
modules.

..  Copyright (c) 2015 by Allen Barker.
    License: MIT, see LICENSE for more details.

"""

from __future__ import print_function, division, absolute_import

ALLOW_USER_CONFIG_FILES = True # Setting False turns off even looking for a config file.
CONFIG_FILE_NAMES = ["pytest_helper.ini"] # List of filenames, searched for in order.
FAIL_ON_MISSING_CONFIG = False # Raise exception if config file enabled but not found.
CONFIG_SECTION_STRING = "pytest_helper" # Label for active section of the config file.

# Pytest-helper saves module-specific information in a dict as a special
# attribute of the modules themselves.  This is the name that is used, saved in
# the modules' namespaces.  Currently not forced to be unique, but maybe should be.
NAME_OF_PYTEST_HELPER_PER_MODULE_INFO_DICT = "_pytest_helper_module_info_320gj97trxR5GA"

#
# Config file locating and reading functions.
#

class PytestHelperException(Exception):
    """Raised by the routines to help with running tests."""
    pass

class LocalsToGlobalsError(PytestHelperException):
    """Raised only when there is an error related to the `locals_to_globals`
    operations.  Inherits from `PytestHelperException`."""
    pass

