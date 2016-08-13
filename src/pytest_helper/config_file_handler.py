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

# TODO: Add tests of the config file stuff.

# TODO, maybe: Add an option to the pytest-helper.conf file which allows for an
# arbitrary directory to be added to the sys.path.  So, in test dir at root of
# repo you can just put in that file for the distribution directory and not
# have to use any other sys_paths command!!!!!!!  LATER when you want to use
# pip local install (when setup.py is set up and you are ready to package) you
# can just delete that line from the file!!!!!!!!!!!!!!!!!!  BUT, the
# difficulty is that any relative files should be relative to that file itself,
# NOT the importing file... should be a fairly easy conversion barring the
# problems with changing the local python directory (needs to be done early, if
# possible).

from __future__ import print_function, division, absolute_import
import inspect
import sys
import os
try:
    from configparser import ConfigParser
except ImportError: # Must be Python 2; use old names.
    from ConfigParser import SafeConfigParser as ConfigParser
import py.test
pytest = py.test # Alias, usable in config files.

from pytest_helper.global_settings import (
        CONFIG_FILE_NAMES, # Filenames for config files, searched in order.
        FAIL_ON_MISSING_CONFIG, # Raise exception if config enabled but not found.
        CONFIG_SECTION_STRING) # Label for active section of the config file.

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
    config.read(filename)

    # Convert the ConfigParser format into a regular dict of dicts.
    config_dict = { s:dict(config.items(s)) for s in config.sections() }

    # Evaluate each string within each config file section.
    for section, subdict in config_dict.items():
        for key, value in subdict.items():
            try:
                config_dict[section][key] = eval(value, globals())
            except NameError: # Raised when a name cannot be found in dict.
                err_string = ("NameError in config file."
                              "\nThe section is '{0}', the key is '{1}',"
                              " and the value is '{2}'."
                              .format(section, key, value))
                print(err_string, file=sys.stderr)
                raise
            except SyntaxError:
                err_string = ("SyntaxError in config file."
                              "\nThe section is '{0}', the key is '{1}',"
                              " and the value is '{2}'."
                              .format(section, key, value))
                print(err_string, file=sys.stderr)
                raise
            #except ValueError: # Raised by ast.literal_eval.
            #    err_string = ("ValueError in config file."
            #                  "\nThe section is '{0}', the key is '{1}',"
            #                  " and the value is '{2}'."
            #                  .format(section, key, value))
            #    print(err_string, file=sys.stderr)
            #    raise

    return config_dict

per_module_config_dict = {} # Cache the config dict for each module by module filename.
config_disabled_modules = {} # Save booleans for which modules look for config.

# Note the below cache precludes dynamically changing the config file, which
# seems like a bad idea to allow anyway but might have uses.
config_dict_cache = {} # Cache config dicts by their full filenames (save space and time).

def get_config(calling_mod_path, calling_mod_dir, disable=False):
    """Return the configuration corresponding to the module with pathname
    `calling_mod_path`.  Return an empty dict if no config is found.  Caches
    its values based on pathnames of module (to avoid problems with `__main__`
    when run as a script) as well as on the pathnames of config files.  If
    nothing is found in the cache, it looks for the file and reads it in if
    possible.  If `disable` is set for a module then it will always return an
    empty config dict for the given module and skip searching for the file."""

    # TODO, maybe: Could speed up even more by using a cache on each pathname
    # up to the config file.  A bit more space but faster.

    cache_key = calling_mod_path # Use pathname to avoid __main__ problems.

    # Disable config files for the module if that flag is set.
    if disable:
        config_disabled_modules[cache_key] = True

    # If module not enabled (by current or prev call with enable=True) return empty.
    if cache_key in config_disabled_modules:
        return {}

    if cache_key in per_module_config_dict: # Look in per-module cache.
        config_dict = per_module_config_dict[cache_key]

    else: # If not in per-module cache, look for a config file.
        config_file_path = get_config_file_pathname(calling_mod_dir)

        if config_file_path in config_dict_cache: # Look in the config dict cache.
            config_dict = config_dict_cache[config_file_path]

        elif config_file_path: # Some path was set.
            config_dict = read_and_eval_config_file(config_file_path)
            config_dict_cache[config_file_path] = config_dict
        else: # Returned None from config_file_path.
            if FAIL_ON_MISSING_CONFIG:
                raise PytestHelperException("Config file specified but"
                        " not found in the directory tree.  At least an"
                        " empty file must be present.")
            else:
                config_dict = {} # Assume it is empty if not found and no fail.

        per_module_config_dict[cache_key] = config_dict # Put in cache for module.

    return config_dict

def get_config_value(config_key, default, calling_mod_path, calling_mod_dir):
    """Return the config value from the config file corresponding to the key
    `config_key`.  Return the value `default` if no config value is set."""
    config_dict = get_config(calling_mod_path, calling_mod_dir)

    if CONFIG_SECTION_STRING in config_dict:
        config_dict = config_dict[CONFIG_SECTION_STRING]
    else:
        return default

    if config_key in config_dict:
        return config_dict[config_key]
    else:
        return default

#
# Test this file when invoked as a script.
#

#init(set_package=False) # TODO remove this or set a real config file in path
if __name__ == "__main__": # This guard is optional, but slightly more efficient.
    pass
    # TODO: cannot run own scripts because of relative import of set_package_attribute
    # Fix or delete this whole part... probably the latter.
    #script_run("../../test", pytest_args="-v")
    #script_run(self_test=True, pytest_args="-v -s", exit=True)

#auto_import(noclobber=False)
#print("skipped is", skip)
#globals()["skip"] = fail
def test_config():
    #fail()
    print("skipped inside fun is", skip)
    #fail()
    skip()

