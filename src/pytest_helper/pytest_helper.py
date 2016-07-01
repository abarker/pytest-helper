# -*- coding: utf-8 -*-
"""
Description
-----------

This module contains helper functions for using the pytest unit testing
framework.

..  Copyright (c) 2015 by Allen Barker.
    License: MIT, see LICENSE for more details.

.. default-role:: code

"""

# TODO Add tests of the config file stuff.

# TODO consider this and what effects it might have:
# https://www.python.org/dev/peps/pep-0008/#imports
# Absolute imports are recommended, as they are usually more readable and
# tend to be better behaved (or at least give better error messages) if the
# import system is incorrectly configured (such as when a directory inside a
# package ends up on sys.path ):

# Possible enhancement: It might be useful to go up the tree to find the
# project root (one above package root), and let that be a keyword arg to
# sys_paths.  E.g.,
#
# pytest_helper.sys_paths(from_proj_root="test")
#
# Is there an efficient way?  Then a top-level tests directory would be easy to
# specify in sys_paths keywords.  BUT, how do you find that?  The top level
# will not have an __init__.py file.  You can go up from a module in the
# package, though, and take the first one without an __init__.py file.  It
# could even be calculated on the fly, and probably would need to be, since
# packages can import other packages, all using pytest-helper.
# 
# What about a general routine to go up the tree and save important data,
# caching based on canonical filenames to reduce future lookup times?  This
# could also set the __PACKAGE__ attribute fairly easily in __main__.  A module
# could also consult the pytest_helper module to find out its own data, such as
# current directory, saving having to look up itself.  More general-purpose
# than just helping run pytest tests.
#
# Add an option to the pytest-helper.conf file which allows for an arbitrary
# directory to be added to the sys.path.  So, in test dir at root of repo you
# can just put in that file for the distribution directory and not have to use
# any other sys_paths command!!!!!!!  LATER when you want to use pip local
# install (when setup.py is set up and you are ready to package) you can just
# delete that line from the file!!!!!!!!!!!!!!!!!!  BUT, the difficulty is that
# any relative files should be relative to that file itself, NOT the importing
# file... should be a fairly easy conversion barring the problems with changing
# the local python directory (needs to be done early, if possible).
#
# TODO: make the set_package option of pytest_helper.init function default
# True if an __init__.py file is found in same directory!  Otherwise, default
# False.  Implementation idea: have a general filesystem info scan first
# that gets the config file *and* gets the info of whether in a package (and
# maybe also subsumes the set_package_attribute() function, too, while
# scanning up the dir tree).

from __future__ import print_function, division, absolute_import
import inspect
import sys
import os
try:
    from configparser import ConfigParser
except ImportError: # Must be Python 2; use old names.
    from ConfigParser import SafeConfigParser as ConfigParser
# import functools # Imported just for the wraps decorator.
from . import set_package_attribute
import py.test
pytest = py.test # Alias, usable in config files.

ALLOW_USER_CONFIG_FILES = True # Setting False turns off even looking for a config file.
CONFIG_FILE_NAMES = ["pytest_helper.ini"] # List of filenames, searched for in order.
FAIL_ON_MISSING_CONFIG = False # Raise exception if config file enabled but not found.
CONFIG_SECTION_STRING = "pytest_helper" # Label for active section of the config file.

def script_run(testfile_paths=None, self_test=False, pytest_args=None,
               calling_mod_name=None, calling_mod_path=None, exit=True,
               always_run=False, level=2):
    """Run pytest on the specified test files when the calling module is run as
    a script.  Using this function requires at least Pytest 2.0.
    
    The argument `testfile_paths` should be either the pathname to a file or
    directory to run pytest on, or else a list of such file paths and directory
    paths.  Any relative paths will be interpreted relative to the directory of
    the module which calls this function.
    
    If `self_test` is `True` then pytest will be run on the file of the calling
    script itself, i.e., tests are assumed to be in the same file as the code
    to test.
    
    Using relative paths can fail in cases where Python's CWD is changed
    between the loading of the calling module and the call of this function.
    (Most programs do not change the CWD like that, or they return it to its
    previous value.)  In those cases you can use the `pytest_helper.init()`
    function just after importing `pytest_helper` or else use absolute pathnames
    
    The `calling_mod_name` argument is a fallback in case the calling
    function's module is not correctly located by introspection.  It is usually
    not required (though it is slightly more efficient).  Use it as:
    `module_name=__name__`.  Similarly for `calling_mod_path`, but that should
    be passed the pathname of the calling module's file.
    
    If `exit` is set false then `sys.exit(0)` will be called after the tests
    finish.  The default is to exit after the tests finish (otherwise when
    tests run from the top of a module are finished the rest of the file
    will still be executed).
    
    If `always_run` is true then tests will be run regardless of whether or not
    the function was called from a script.
    
    The parameter `level` is the level up the calling stack to look for the
    calling module and should not usually need to be set."""

    mod_info = get_calling_module_info(module_name=calling_mod_name,
                                       module_path=calling_mod_path, level=level)
    calling_mod_name, calling_mod, calling_mod_path, calling_mod_dir = mod_info

    if calling_mod_name != "__main__":
        if not always_run: return

    # Override arguments with any values set in the config file.
    pytest_args = get_config_value("script_run_pytest_args", pytest_args,
                                             calling_mod_path, calling_mod_dir)

    if isinstance(testfile_paths, str):
        testfile_paths = [testfile_paths]
    elif testfile_paths is None:
        testfile_paths = []

    if self_test:
        testfile_paths.append(calling_mod_path)

    testfile_paths = [os.path.expanduser(p) for p in testfile_paths]
    testfile_paths = [expand_relative(p, calling_mod_dir) for p in testfile_paths]

    # Generate calling string and call pytest on the file.
    for t in testfile_paths:
        pytest_string = t
        if pytest_args:
            pytest_string = pytest_args + " " + pytest_string

        # Call pytest; this requires pytest 2.0 or greater.
        py.test.main(pytest_string)

    if exit:
        sys.exit(0)
    return

previous_sys_path_list = None # Save the sys.path before modifying it, to restore it.

def sys_path(dirs_to_add=None, add_parent=False, add_grandparent=False,
             add_gn_parent=False, add_self=False, calling_mod_name=None, 
             calling_mod_path=None, level=2):
    """Add the canonical absolute pathname of each directory in the list
    `dirs_to_add` to `sys.path` (but only if it isn't there already).  A single
    string representing a path can also be passed to `dirs_to_add`.  Relative
    pathnames are always interpreted relative to the directory of the calling
    module (i.e., the directory of the module that calls this function).
    
    The keyword arguments `add_parent` and `add_grandparent` are shortcuts that
    can be used instead of putting the equivalent relative path on the list
    `dirs_to_add`.  If the keyword argument `add_gn_parent` is set to a
    non-negative integer `n` then the (grand)\ :sup:`n`\ parent is added to the
    path, where (grand)\ :sup:`1`\ parent is the grandparent.  If `add_self` is
    true then the directory of the calling module is added to the system
    `sys.path` list.
    
    The parameters `calling_mod_name` and `calling_mod_dir` can be set as a
    fallback in case the introspection for finding the calling module's
    information fails for some reason.  The parameter `level` is the level up
    the calling stack to look for the calling module and should not usually
    need to be set."""

    # We really only need calling_mod_dir as a fallback *except* when config
    # files are used we also need to know the module path, since config info
    # is looked up and saved per-module.
    mod_info = get_calling_module_info(module_name=calling_mod_name,
                                       module_path=calling_mod_path, level=level)
    calling_mod_name, calling_mod, calling_mod_path, calling_mod_dir = mod_info

    # Override arguments with any values set in the config file.
    # TODO what if you want more than one gn parent?  Could take list of numbers?
    add_gn_parent = get_config_value("sys_path_add_gn_parent", add_gn_parent,
                                             calling_mod_path, calling_mod_dir)
    # Get the config file extra paths; note added to *end* of list above, but
    # all are inserted, so the last ones come later in the sys.path list.
    # TODO: needs more consideration, see paragraph near top.
    #config_always_add_paths = get_config_value("sys_path_always_add", [],
    #                                         calling_mod_path, calling_mod_dir)

    if dirs_to_add is None: dirs_to_add = []
    if isinstance(dirs_to_add, str): dirs_to_add = [dirs_to_add]
    if add_parent:
        dirs_to_add.append("..")
    if add_grandparent:
        dirs_to_add.append(os.path.join("..",".."))
    if add_gn_parent is not False:
        try:
            g_level = int(add_gn_parent)
        except TypeError:
            raise PytestHelperException("Non-integer argument to the add_gn_parent "
                    "argument of the pytest_helper.sys_path function.")
        if g_level < 0 or add_gn_parent is True:
            raise PytestHelperException("Negative argument or literal True argument\n"
                  "to the add_gn_parent parameter of the pytest_helper.sys_path"
                  " function.\nIt must be a non-negative integer.")
        parent_string = ".."
        for i in range(g_level):
            parent_string = os.path.join(parent_string, "..")
        dirs_to_add.append(parent_string)
    if add_self:
        dirs_to_add.append(".")

    #dirs_to_add.extend[config_always_add_paths] # Extend with the config file list.

    dirs_to_add = [os.path.expanduser(p) for p in dirs_to_add]

    global previous_sys_path_list
    previous_sys_path_list = sys.path[:]

    for path in dirs_to_add:
        if os.path.isabs(path):
            path = os.path.realpath(path) # Convert to canonical path.
            if path not in sys.path:
                sys.path.insert(0, path)
        else:
            joined_path = expand_relative(path, calling_mod_dir)
            if joined_path not in sys.path:
                sys.path.insert(0, joined_path)

    return

def restore_previous_sys_path():
    """This function undoes the effect of the last call to `sys_path`, returning
    `sys.path` to its previous, saved value.  This can be useful at times."""
    global previous_sys_path_list
    if previous_sys_path_list is not None:
        sys.path = previous_sys_path_list
        previous_sys_path_list = None
    return


def init(set_package=False, conf=True, calling_mod_name=None,
                                        calling_mod_path=None, level=2):
    """A function to initialize the `pytest_helper` module just after importing
    it.  This function is currently only necessary in rare cases where Python's
    current working directory (CWD) is changed between the time when the
    executing module is first loaded and when `script_run` or `sys_path` is
    called from that module.  In those cases the module's pathname relative to
    the previous CWD will be incorrectly expanded relative to the new CWD.
    Calling this function causes the earlier expanded pathname to be cached.
    This function should be called before any function call or import which
    changes the CWD and which doesn't change it back afterward.  Importing
    `pytest_helper` just after the system imports and then immediately calling
    this function should work.
    
    The `init` function takes an optional keyword argument `set_package`.  If
    it is true then the package attribute of module `__main__` will be
    automatically set.  This allows for using relative imports fromp scripts,
    but it must be called before the relative imports are attempted.  The
    function call `pytest_helper.init(set_package=True)` is equivalent to::
        
        pytest_helper.init()
        import set_package_attribute
       
    If the parameter `conf` is set false then no configuration files will be
    searched for or used.
    """
    # TODO:  update docs above, no longer separate import

    # The get_calling_module_info function caches module info, including the
    # calling_mod_path, as a side effect.
    mod_info = get_calling_module_info(module_name=calling_mod_name,
                                       module_path=calling_mod_path, level=level)
    calling_mod_name, calling_mod, calling_mod_path, calling_mod_dir = mod_info

    # Disable the configuration file if requested.
    if not conf or not ALLOW_USER_CONFIG_FILES:
        get_config(calling_mod_path, calling_mod_dir, disable=True)

    # Override arguments with any values set in the config file.
    set_package = get_config_value("init_set_package", set_package,
                                             calling_mod_path, calling_mod_dir)

    if set_package:
       # Set the __PACKAGE__ attribute for module __main__ (if there is one).
       set_package_attribute.set_package_attribute()

    return

#
# Functions for copying locals to globals.
#

# The last copied attributes are saved in the same globals dict where they were
# copied to, in a list with this attribute name.
last_saved_list_name = "pytest_helper_last_copied_320gj97tr"

def locals_to_globals(fun_locals=None, fun_globals=None, auto_clear=True, 
                      noclobber=True, level=2):
    """Copy all local variables in the calling function's local scope to the
    global scope of the module where that function was called.  The function's
    parameters are ignored and are not copied.  This routine should only be
    called once, near the end of a test function or fixture.  It allows for
    variables to be shared with another test function as globals.  This
    function does not allow any existing global variables to be overwritten
    unless they were either set by a previous run of this function or
    `noclobber` is false.  A `LocalsToGlobalsError` will be raised on any
    attempt to overwrite an existing global variable.  This avoids accidentally
    overwriting important global attributes.
    
    This routine's effect is similar to the effect of explicitly declaring each
    of a function's variables to be `global`, or doing
    `globals().update(locals())`, except that it 1) ignores local variables
    which are function parameters, 2) adds more error checks, and 3) clears any
    previously-set values.
    
    Note that the globals set with `locals_to_globals` can be accessed and used
    in any function in the module, but they are still read-only (as usual with
    globals).  An attribute must be explicitly declared `global` in order to
    modify the global value.  (it is then no longer local to the function so
    the next calls to `locals_to_globals` will clear it but not set it).  If
    `locals_to_globals` set it before, though, it will still be deleted when
    `locals_to_globals` is called again with default `auto_clear` or
    `clear_locals_from_globals` is called.
    
    If `auto_clear` is true (the default) then any variable that was set on the
    last run of this function will be automatically cleared before any new ones
    are set.  This avoids "false positives" where a later test succeeds only
    because of a global left over from a previous test.  Note that this clears
    globals on the saved list of globals even if their values were later
    modified.  If `auto_clear` is false then `clear_locals_from_globals` must
    be explicitly called before calling this function again (or else a
    `LocalsToGlobalsError` will be raised).
    
    The argument `fun_locals` can be used as a fallback to pass the `locals()`
    dict from the function in case the introspection technique does not work
    for some reason.  The `fun_globals` argument can similarly be passed
    globals() as a fallback.  So you could call::

       locals_to_globals(locals(), globals())
       
    to bypass the introspection used to locate the two dicts.
    
    The `level` argument is the level up the calling stack to look for the
    calling function.  In order to call an intermediate function which then
    calls this function, for example, `level` would need to be increased by
    one."""

    #view_locals_up_stack(4) # useful for debugging

    if not fun_locals:
        fun_locals = get_calling_fun_locals_dict(level)
    if not fun_globals:
        fun_globals = get_calling_fun_globals_dict(level)

    if last_saved_list_name in fun_globals:
        last_copied_names = fun_globals[last_saved_list_name]
    else:
        last_copied_names = []
        fun_globals[last_saved_list_name] = last_copied_names

    # If last_copied_names isn't empty assume the user forgot to clear it.
    if last_copied_names:
        if auto_clear:
            clear_locals_from_globals(level=level+1) # One extra level from this fun.
        else:
            raise LocalsToGlobalsError("Failure to call clear_locals_from_globals()"
                                      " after previous copy (auto_clear is False).")

    # Get the function's parameters so we can ignore them as locals.
    params, values = get_calling_fun_parameters(level)

    # Do the actual copies.
    for k, v in fun_locals.items():
        if k in params: continue
        # The following line filters out some weird pytest vars starting with @.
        if not (k[0].isalpha() or k[0] == "_"): continue
        if k in fun_globals and noclobber:
            raise LocalsToGlobalsError("Attempt to overwrite existing "
                                       "module-global variable: " + k)
        fun_globals[k] = fun_locals[k]
        last_copied_names.append(k)
    return

def clear_locals_from_globals(level=2):
    """Clear all the global variables that were added by locals_to_globals.
    This is called automatically by `locals_to_globals` unless that function
    is run with `auto_clear` set false.  This only affects the module from
    which the function is called."""
    g = get_calling_fun_globals_dict(level)
    last_copied_names = g[last_saved_list_name]
    for k in last_copied_names:
        try:
            del g[k]
        except KeyError:
            pass # Ignore if not there.
    del last_copied_names[:] # Empty out last_copied_names in place.

class PytestHelperException(Exception):
    """Raised by the routines to help with running tests."""
    pass

class LocalsToGlobalsError(PytestHelperException):
    """Raised only when there is an error related to the `locals_to_globals`
    operations."""
    pass

AUTO_IMPORT_DEFAULTS = [("pytest", py.test), # (<nameToImportAs>, <value>)
                        ("raises", py.test.raises),
                        ("fail", py.test.fail),
                        ("fixture", py.test.fixture),
                        ("skip", py.test.skip),
                        ("xfail", py.test.xfail),
                        ("locals_to_globals", locals_to_globals),
                        ("clear_locals_from_globals", clear_locals_from_globals)
                       ]

def auto_import(noclobber=True, skip=None, imports=AUTO_IMPORT_DEFAULTS,
                calling_mod_name=None, calling_mod_path=None, level=2):
    """This function imports some pytest-helper and pytest attributes into the
    calling module's global namespace.  This avoids having to explicitly do
    common imports.  A `PytestHelperException` will be raised if any of those
    globals already exist, unless `noclobber` is set false.

    The `imports` option is a list of (name,value) pairs to import
    automatically.  Since using it each time would be as much trouble as doing
    the imports, explicitly, it is mainly meant to be set in configuration
    files.  In a config file the values are evaluated in the global namespace
    of `pytest_helper`.  The `skip` option is a list of names to skip in
    importing, if just one or two are causing problems locally to a file.
    
    The default variables that are imported from the `pytest_helper` module are
    `locals_to_globals`, and `clear_locals_from_globals`.  The module `py.test`
    is imported as the single name `pytest`.  The functions from pytest that
    are imported by default are `raises`, `fail`, `fixture`, and `skip`, and
    `xfail`."""

    mod_info = get_calling_module_info(module_name=calling_mod_name,
                                       module_path=calling_mod_path, level=level)
    calling_mod_name, calling_mod, calling_mod_path, calling_mod_dir = mod_info

    # Override arguments with any values set in the config file.
    noclobber = get_config_value("autoimport_noclobber", noclobber,
                                             calling_mod_path, calling_mod_dir)
    imports = get_config_value("autoimport_imports", imports,
                                             calling_mod_path, calling_mod_dir)
    skip = get_config_value("autoimport_skip", skip,
                                             calling_mod_path, calling_mod_dir)

    def insert_in_dict(d, name, value, noclobber):
        """Insert (name, value) in dict d checking for noclobber."""
        if noclobber and name in d:
            raise PytestHelperException("The pytest_helper function auto_import"
                    "\nattempted an overwrite with noclobber set.  The attribute"
                    " is: " + name)
        d[name] = value

    g = get_calling_fun_globals_dict(level=level)

    for name, value in imports:
        if skip and name in skip: continue
        insert_in_dict(g, name, value, noclobber)

    return

#
# Utility functions.
#

def expand_relative(path, basepath):
    """Expand the path `path` relative to the path `basepath`.  If `basepath`
    is not an absolute path it is first expanded relative to Python's current
    CWD to be one.  The canonical version of the absolute path is returned."""
    path = os.path.expanduser(path)
    if os.path.isabs(path):
        return os.path.realpath(path) # Return canonical path, already absolute.
    if not os.path.isabs(basepath):
        basepath = os.path.realpath(os.path.abspath(basepath))
    joined_path = os.path.realpath(os.path.abspath(os.path.join(basepath, path)))
    return joined_path

# The levels used in the utility routines below are levels in the calling stack
# (examined using inspect).  The level number includes the level of the utility
# function itself.  So level 0 is the attribute of the utility function itself,
# level 1 is the attribute of the calling function, level 2 is the function
# that called the calling function, etc.

module_info_cache = {} # Save info on modules, keyed on module names.

def get_calling_module_info(level=2, check_exists=True,
                            module_name=None, module_path=None):
    """A higher-level routine to get information about the module of a function
    back some number of levels in the call stack (the calling function).
    Returns a tuple::

       (calling_module_name,
        calling_module,
        calling_module_path,
        calling_module_dir)
    
    Any relative paths are converted to absolute paths.  If `check_exists` is
    true then a check is made to make sure that the module actually exists at
    the path.
    
    Absolute paths are cached in a dict keyed on module names so we always get
    the pathname calculated on the first call to this program from a given
    module.  This is important in cases where the CWD is changed between the
    initial loading time for a module and the time it (indirectly) calls this
    routine.  Such problems are rare, but if they occur you can use these two
    lines near the top of the module (before any imports which might change
    CWD)::

       import pytest_helper
       pytest_helper.get_calling_module_info(level=1)

    The module name and/or path can be supplied via the keyword arguments if
    introspection still fails for some reason (or just to slightly improve
    efficiency)."""
    # Note that caching is done with the fully qualified module names.
    # Not everything can be cached, but the calling_module_dir is
    # one thing that is cached.  The cache key is the calling module name.
    # TODO: note that __main__ module will not be cached the same as
    # when run from pytest with its normal name.

    if module_name:
        calling_module_name = module_name
        calling_module = sys.modules[calling_module_name]
    else:
        # Call low-level routine to do the introspection.
        calling_module_name, calling_module = get_calling_module(level)

    if module_path:
        calling_module_path = module_path
    elif calling_module_name in module_info_cache:
        return module_info_cache[calling_module_name]
    else:
        calling_module_path = os.path.realpath(
                                   os.path.abspath(calling_module.__file__))

    calling_module_dir = os.path.dirname(calling_module_path)

    # Do an error check to make sure that the detected module directory exists.
    if check_exists and not os.path.isdir(calling_module_dir):
        raise PytestHelperException("\n\nThe directory\n   {0}\nof the detected"
                " calling module does not exist.\nDid the Python CWD change without"
                " being changed back?\nYou can try importing pytest_helper near the"
                " top\nof your file and then immediately calling\n"
                "   pytest_helper.init()\nafterward.  If"
                " necessary you can set `module_name` and\n`module_path`"
                " explicitly from keyword arguments.".format(calling_module_dir))

    module_info = (calling_module_name, calling_module,
                   calling_module_path, calling_module_dir)

    module_info_cache[calling_module_name] = module_info
    return module_info

def view_locals_up_stack(num_levels=4):
    """To get an idea of what things look like.  Run from somewhere and see."""
    print("Viewing local variable dict keys up the stack.\n")
    for i in reversed(range(num_levels)):
        calling_fun_frame = inspect.stack()[i][0]
        calling_fun_name = inspect.stack()[i][3]
        calling_fun_locals = calling_fun_frame.f_locals
        indent = "   " * (num_levels - i)
        print("{0}{1} -- stack level {2}".format(indent, calling_fun_name, i))
        print("{0}f_locals keys: {1}\n".format(indent, calling_fun_locals.keys()))

def show_globals(level=2, filt=True):
    """Prints the module globals for the module the calling function was called
    in, filtering out files starting with '__'.  Useful for testing."""
    print("Globals:")
    g = get_calling_fun_globals_dict(level)
    for k, v in sorted(g.items()):
        if filt and k.startswith("__"): continue
        print("    {0} = {1}".format(k, v))

def get_calling_fun_parameters(level=2):
    """Note that in calling this function you have to increase the level by
    one since it is also on the stack when it does the lookup.
       level 0: This function.
       level 1: The frame of the function that called this function.
       level 2: The frame of the function that called the calling function."""
    calling_fun_frame = inspect.stack()[level][0]
    params, _, _, values = inspect.getargvalues(calling_fun_frame)
    return (params, values)

def get_calling_fun_locals_dict(level=2):
    """Note that in calling this function you have to increase the level by
    one since it is also on the stack when it does the lookup.
       level 0: The locals dict of this function.
       level 1: The locals dict of the function that called this function.
       level 2: The locals dict of the function that called the calling function."""
    calling_fun_frame = inspect.stack()[level][0]
    calling_fun_locals = calling_fun_frame.f_locals
    return calling_fun_locals

def get_calling_fun_globals_dict(level=2):
    """Note that in calling this function you have to increase the level by
    one since it is also on the stack when it does the lookup.
       level 0: The globals dict of this function.
       level 1: The globals dict of the function that called this function.
       level 2: The globals dict of the function that called the calling function."""
    calling_fun_frame = inspect.stack()[level][0]
    calling_fun_globals = calling_fun_frame.f_globals
    return calling_fun_globals

def get_calling_module(level=2):
    """Run this inside a function.  Get the module where the current function
    is being called from.  Returns a tuple (mod_name, module) with the name of
    the module and the module itself.  Note that the module name may be relative
    (to the CWD when the module was loaded) or absolute.  For some info on the
    introspection methods used, see stackoverflow.com/questions/1095543/.
       level 0: Module for this function.
       level 1: Module for the function calling this one (what you usually want).
       level 2: Module for the function that called the one calling this one.

    This is a low-level routine; higher-level functions should usually
    call `get_calling_module_info` instead, which caches its data.

    The returned module name is the fully qualified name, except in the
    case of `__main__`.
    """
    # Three lines below work, even when chdir is called; just get __name__ from
    # the globals dict.
    calling_fun_globals = get_calling_fun_globals_dict(level=level+2)
    calling_module_name = calling_fun_globals["__name__"]
    calling_module = sys.modules[calling_module_name]

    # Two lines below work.  They fail, though, when os.chdir("..") is called
    # before this function is called.
    #frame = inspect.stack()[level+1]
    #calling_module = inspect.getmodule(frame[0])

    # Four lines below work, using sys rather than inspect.
    # Someone says this way works with pyinstaller, too, but I haven't tried it.
    # Apparently sys._getframe is available with a performance hit in PyPy,
    # but sys._current_frames is less widely available.
    #f = list(sys._current_frames().values())[0]
    #for i in range(level): f = f.f_back
    #calling_module_name = f.f_globals['__name__']
    #calling_module = sys.modules[calling_module_name]

    return calling_module.__name__, calling_module

#
# Config file locating and reading functions.
#

def get_importing_module_filename(level=2):
    """Run this during the initialization of a module to return the absolute pathname
    of the module which is importing the module that is currently being imported."""
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
    script_run("../test", pytest_args="-v")
    #script_run(self_test=True, pytest_args="-v -s", exit=True)

#auto_import(noclobber=False)
#print("skipped is", skip)
#globals()["skip"] = fail
def test_config():
    #fail()
    print("skipped inside fun is", skip)
    #fail()
    skip()

