#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Import this pytest_helper function to test it and to have a dummy function
to import with relative imports and test that.
"""
from __future__ import print_function, division, absolute_import
import pytest_helper

def check_calling_get_module_info(level):
    print(pytest_helper.get_calling_module_info(level=level)[0])
    return pytest_helper.get_calling_module_info(level=level)[0]

