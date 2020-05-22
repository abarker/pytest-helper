# -*- coding: utf-8 -*-
"""
Description
-----------

This module contains all the code for searching for, caching, and implementing
config files.

..  Copyright (c) 2015 by Allen Barker.
    License: MIT, see LICENSE for more details.

.. default-role:: code

"""

# TODO: Where possible switch from the saved dict in this namespace to saving
# in the per-module info dict.

# TODO: Add tests of the config file stuff.

# TODO, maybe: Add an option to the pytest-helper.conf file which allows for an
# arbitrary directory to be added to the sys.path.  So, in test dir at root of
# repo you can just put in that file for the distribution directory and not
# have to use any other sys_paths command.  LATER when you want to use pip
# local install (when setup.py is set up and you are ready to package) you can
# just delete that line from the file.  BUT, the difficulty is that any
# relative files should be relative to that file itself, NOT the importing
# file... should be a fairly easy conversion barring the problems with changing
# the local python directory (needs to be done early, if possible).

from __future__ import print_function, division, absolute_import
import inspect
import sys
import os
import ast
try:
    from configparser import ConfigParser
except ImportError: # Must be Python 2; use old names.
    from ConfigParser import SafeConfigParser as ConfigParser

from pytest_helper.global_settings import (
        PytestHelperException,
        CONFIG_FILE_NAMES, # Filenames for config files, searched in order.
        FAIL_ON_MISSING_CONFIG, # Raise exception if config enabled but not found.
        CONFIG_SECTION_STRING, # Label for active section of the config file.
        NAME_OF_PYTEST_HELPER_PER_MODULE_INFO_DICT)

#
# Config file locating and reading functions.
#

def get_importing_module_filename(level=2):
    """Run this during the initialization of a module to return the absolute pathname
    of the module that it is being imported from."""
    module_filename = inspect.getframeinfo(
                      inspect.getouterframes(inspect.currentframe())[level][0])[0]
    return os.path.abspath(module_filename)

def get_config_file_pathname(calling_mod_dir):
    """Get the full pathname of the configuration file, returning `None` if
    nothing was found.  Go up the directory tree starting at
    `calling_mod_dir`, taking the first file found with an allowed name.  If
    no package are encountered by the top-level root directory, return
    `None`."""
    stop_at_package_top = False # Whether to stop search after package top.

    dirname = calling_mod_dir # Start looking in calling module's dir.

    # Go up the directory tree.
    in_package = False
    while True:
        if os.path.exists(os.path.join(dirname, "__init__.py")):
            in_package = True

        for config_name in CONFIG_FILE_NAMES:
            config_path = os.path.join(dirname, config_name)
            if os.path.exists(config_path):
                return config_path

        dirname, name = os.path.split(dirname) # Go up one dir.

        if not name: # If no subdir name then we were at root dir.
            return None
        if stop_at_package_top and in_package and not os.path.exists(
                                   os.path.join(dirname, "__init__.py")):
            return None # Past the top of a package, nothing found.


def read_and_eval_config_file(filename):
    """Return a dict of dicts containing a dict of parameter arguments for each
    section of the config file, with the evaluated value."""

    config = ConfigParser()
    try:
        config.read(filename)
    except SyntaxError:
        print("Error in reading the pytest-helper config file named '{0}'"
                .format(filename), file=sys.stderr)
        raise

    # Convert the ConfigParser format into a regular dict of dicts.
    config_dict = {s:dict(config.items(s)) for s in config.sections()}

    # Evaluate each string within each config file section.
    for section, subdict in config_dict.items():
        for key, value in subdict.items():
            try:
                config_dict[section][key] = ast.literal_eval(value)
            except (ValueError, SyntaxError):
                raise PytestHelperException("Error in evaluating the config"
                        " file '{0}'.  Error in section '{1}' on the key '{2}' with"
                        " value '{3}'."
                        .format(filename, section, key, value))

    return config_dict


# Note the below cache precludes dynamically changing the config file, which
# seems like a bad idea to allow anyway but might have uses.
config_dict_cache = {} # Cache config dicts by their full filenames (save space and time).

def get_config(calling_mod, calling_mod_dir, disable=False):
    """Return the configuration corresponding to the module `calling_mod`.
    Return an empty dict if no config is found.  Caches its values in the
    namespace of the modules (in the pytest-helper data dict).  Also caches
    config files based on their pathnames.  If nothing is found in the cache,
    it looks for the file and reads it in if possible.  If `disable` is set for
    a module then `get_config` will always return an empty config dict for the
    given module and skip searching for the file."""

    # TODO, maybe: Could speed up even more by using a cache on each pathname
    # up to the config file.  A bit more space but faster.

    if not hasattr(calling_mod, NAME_OF_PYTEST_HELPER_PER_MODULE_INFO_DICT):
        setattr(calling_mod, NAME_OF_PYTEST_HELPER_PER_MODULE_INFO_DICT, {})
    module_info_dict = getattr(calling_mod, NAME_OF_PYTEST_HELPER_PER_MODULE_INFO_DICT)

    if "config_data_dict" not in module_info_dict:
        # Search for a file if the key is not set.
        config_file_path = get_config_file_pathname(calling_mod_dir)

        if config_file_path in config_dict_cache: # Look in the config dict cache.
            config_data_dict = config_dict_cache[config_file_path]

        elif config_file_path: # Some path was set.
            config_data_dict = read_and_eval_config_file(config_file_path)
            config_dict_cache[config_file_path] = config_data_dict
        else: # Returned None from config_file_path.
            if FAIL_ON_MISSING_CONFIG:
                raise PytestHelperException("Config file specified but"
                        " not found in the directory tree.  At least an"
                        " empty file must be present.")
            else:
                config_data_dict = {} # Assume it is empty if not found and no fail.
        module_info_dict["config_data_dict"] = config_data_dict
    else:
        config_data_dict = module_info_dict["config_data_dict"]

    if "config_disabled" not in config_data_dict:
        config_data_dict["config_disabled"] = False

    # Disable config files for the module if that flag is set.
    if disable:
        config_data_dict["config_disabled"] = True

    # If module not enabled (by current or prev call with enable=True) return empty.
    if config_data_dict["config_disabled"]:
        return {}

    return config_data_dict

def get_config_value(config_key, default, calling_mod, calling_mod_dir):
    """Return the config value from the config file corresponding to the key
    `config_key`.  Return the value `default` if no config value is set.
    This is called in the main functions to get defaults."""
    config_dict = get_config(calling_mod, calling_mod_dir)

    if CONFIG_SECTION_STRING in config_dict:
        config_dict = config_dict[CONFIG_SECTION_STRING]
    else:
        return default

    if config_key in config_dict:
        return config_dict[config_key]
    else:
        return default


