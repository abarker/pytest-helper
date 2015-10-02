# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
import inspect
import sys
import os
from py.test import raises, fail, fixture, skip
import py.test

"""

Helper functions for using pytest.

This stuff here is unorganized and maybe out-of-date, but the docstrings
below are correct.  Fix this stuff up, write a markdown description, too,
at some point.  Maybe use some kind of literate auto-doc system like in
scikit-learn modules, and generate a static page.

Note that with script_run the script is run twice (at least the init) unless
the call is put near the top of the file (may be bad for long-running init
things).

You could always test the __name__="__main__" twice, it wouldn't really matter.
Can optionally add that around script_run.  So while it is checked for main
inside it, make clear to users that they can put the code inside a test like
that, too (for clarity or slight efficiency gain).

This package provides:

      script_run
      auto_import
      sys_path
      save_abspath

      locals_to_globals
      clear_locals_from_globals


Remember that using locals() and globals() is preferred for getting the
variable dicts when within the same frame.

Note it needs at least Pytest 2.0.

Note one advantage of specifications of test files and dirs to import is that
relative paths are always relative to the calling module location, not the
Python CWD (which can change depending on where the program is run from).
Using relative paths improves portability.

Note that problems with relative paths can arise due to starting scripts or
the Python interpreter from different directories.  Interpreting all paths
relative to the calling file's location eliminates this problem.

Note that you can pass in directory names, too.

Note that only the script_run routine is really dependent on pytest.

Possible later improvements:
   - Allow multiple test files to be run, with optional list of testfiles.
   - Have an option named "show_commands" which just prints out the commands
     that are run and then exits.  So people could easily go back to the
     rote way if necessary on some system, and the curious could see what's
     going on behind the scenes.

"""

def script_run(testfile_paths=None, self_test=False, pytest_args=None,
               calling_mod_name=None, calling_mod_path=None, exit=True):
    """Run pytest when the calling module is running as a script.
    Run pytest on the test file when the calling module is run as a script.
    
    The argument `testfile_paths` should be either the pathname to a file or
    directory to run pytest on, or a list of such file paths and directory
    paths.  Any relative paths will be interpreted relative to the directory of
    the script which calls this function.
    
    If `self_test` is `True` then pytest will be run on the file of the calling
    script itself, i.e., tests are assumed to be in the same file as the code
    to test.
    
    Using relative paths can fail in cases where Python's CWD is changed
    between the loading of the calling module and the call of this function.
    (Most programs do not change the CWD like that, or they return it to its
    previous value.)  In those cases you can still use absolute pathnames.
    
    The `calling_mod_name` argument is a fallback in case the calling
    function's module is not correctly located by introspection.  It is usually
    not required (though it is slightly more efficient).  Use it as:
    `module_name=__name__`.  Similarly for `calling_mod_path`, but that should
    be passed the pathname of the calling module's file.
    
    If `exit` is set false then `sys.exit(0)` will be called after the tests
    finish.  The default is to exit after the tests finish."""

    mod_info = get_calling_module_info(module_name=calling_mod_name,
                                       module_path=calling_mod_path, level=2)
    calling_mod_name, calling_mod, calling_mod_path, calling_mod_dir = mod_info

    if calling_mod_name != "__main__": # Only run if __main__ is calling module.
        return

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

def sys_path(dirs_to_add=None, add_parent=False, add_grandparent=False,
              calling_mod_dir=None, level=2):

    """Add each directory in the list `dirs_to_add` to `sys.path` (but only if
    the absolute path isn't there already).  A single string representing a
    path can also be passed to `dirs_to_add`.  Relative pathnames are always
    interpreted relative to the directory of the calling module (i.e., the
    directory of the module that calls this function).
    
    The keywords `add_parent` and `add_grandparent` are shortcuts that can be
    used instead of putting the relative path on the list `dirs_to_add`.
    
    The parameter `calling_mod_dir` can be set as a fallback in case the
    introspection for finding the calling module's directory fails for some
    reason.  The `level` is the level up the calling stack to look for the
    calling module."""

    if not calling_mod_dir:
        calling_mod_dir = get_calling_module_info()[3]
        print("in sys_path, calling_mod_dir is", calling_mod_dir)

    if dirs_to_add is None:
        dirs_to_add = []
    if isinstance(dirs_to_add, str):
        dirs_to_add = [dirs_to_add]
    if add_parent:
        dirs_to_add.append("..")
    if add_grandparent:
        dirs_to_add.append(os.path.join("..",".."))

    dirs_to_add = [os.path.expanduser(p) for p in dirs_to_add]

    #sys.path.insert(0, calling_mod_dir) # Add testfile dir to sys.path NEEDED OR DELETE?

    for path in dirs_to_add:
        if os.path.isabs(path):
            if path not in sys.path:
                sys.path.insert(0, path)
        else:
            joined_path = expand_relative(path, calling_mod_dir)
            if joined_path not in sys.path:
                sys.path.insert(0, joined_path)
    return

def auto_import(noclobber=True, level=2):
    """ This function will import some pytest_helper and pytest attributes into
    the calling module's global namespace.  That avoids having to explicitly
    import things like `locals_to_globals`, `skip`, `raises`, and `fail`.  A
    `PytestHelperException` will be raised if any of those globals already
    exist, unless `noclobber` is set false."""
    # TODO maybe have some options to turn on and off certain groups of autoimports.

    def insert_in_dict(d, name, value):
        """Insert (name, value) in dict d checking for noclobber."""
        if noclobber and name in d:
            raise PytestHelperException("The pytest_helper function auto_import"
                    "\nattempted an overwrite with noclobber set.  The attribute"
                    " is: " + name)
        d[name] = value

    g = get_calling_fun_globals_dict(level=level)

    # Pytest itself, imported as pytest, not py.test
    insert_in_dict(g, "pytest", py.test)

    # Functions from pytest.
    insert_in_dict(g, "raises", raises)
    insert_in_dict(g, "fail", fail)
    insert_in_dict(g, "fixture", fixture)
    insert_in_dict(g, "skip", skip)

    # Functions and classes from this module.
    insert_in_dict(g, "script_run", script_run)
    insert_in_dict(g, "sys_path", sys_path)
    insert_in_dict(g, "save_abspath", save_abspath)
    insert_in_dict(g, "locals_to_globals", locals_to_globals)
    insert_in_dict(g, "clear_locals_from_globals", clear_locals_from_globals)
    return

def save_abspath():
    """This function is only necessary in rare cases where Python's current
    working directory (CWD) is changed between the time when pytest_helper is
    loaded and when `script_run` or `sys_path` is called.  In those cases
    expanding relative pathnames from before the CWD into absolute pathnames
    will fail.  This function should be called before any function call or
    import which changes the CWD and which doesn't change it back afterward.
    Importing pytest_helper just after the system imports and then immediately
    calling this function should work."""
    get_calling_module_info(level=2) # This caches the module info.
    return

#
# Functions for copying locals to globals.
#

last_copied_names = [] # Saves the most-recently-copied attribute names. 
context_marker = "pytest_helper_context_marker_320gj97tr" # Detect new global context.

def locals_to_globals(fun_locals=None, fun_globals=None, auto_clear=True, level=2):

    """Copy all local variables in the calling function's local scope to the
    global scope of the module where that function was called.  The function's
    parameters are ignored and are not copied.  This routine should be called
    near the end of a function.  It does not allow any existing global
    variables to be overwritten (and will raise `LocalsToGlobalsError` on any
    attempt to do so).  This avoids accidentally overwriting important global
    attributes.
    
    This routine's effect is similar to the effect of explicitly declaring all
    of a function's variables to be `global`, or doing
    `globals().update(locals())`, except that it ignores parameters, adds more
    error checks, and clears any previously-set values.  Note that the globals
    can be accessed and used in any function, but they are read-only.  If an
    attribute is explicitly declared `global` in order to modify it, then it
    will no longer be local so further calls to `locals_to_globals` will not
    save it (this should not occur in most testing setups, but it is worth
    noting).  If `locals_to_globals` set it before, though, it will still be
    deleted when `locals_to_globals` is called again with default `auto_clear`
    or `clear_locals_from_globals` is called.
    
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
    globals() as a fallback.  So you could call
       `locals_to_globals(locals(), globals())`
    to bypass the introspection.
    
    The `level` argument is the level up the calling stack to look for the
    calling function.  In order to call an intermediate function which then
    calls this function, for example, `level` would need to be increased by
    one."""
    #view_locals_up_stack(4) # useful for debugging
    global last_copied_names

    if not fun_locals:
        fun_locals = get_calling_fun_locals_dict(level)
    if not fun_globals:
        fun_globals = get_calling_fun_globals_dict(level)

    # If we have a new global context (i.e., the context marker previously set
    # is not in globals), reset the copied names list.  This is a paranoid
    # test, run just in case Pytest might decide to create a new context.
    if not context_marker in fun_globals:
        last_copied_names = []
        fun_globals[context_marker] = True

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
        if k in fun_globals:
            raise LocalsToGlobalsError("Attempt to overwrite existing "
                                       "module-global variable: " + k)
        # The below line should write to the dotted module name instead, to work
        # when run from a different module.
        #exec("global {0}\n{0}=v".format(k), globals(), locals())
        fun_globals[k] = fun_locals[k] # works
        last_copied_names.append(k)
    return

def clear_locals_from_globals(level=2):
    """Clear all the global variables that were added by locals_to_globals."""
    global last_copied_names
    g = get_calling_fun_globals_dict(level)
    for k in last_copied_names:
        try:
            del g[k]
        except KeyError:
            pass # Ignore if not there.
    last_copied_names = []

class PytestHelperException(Exception):
    pass

class LocalsToGlobalsError(PytestHelperException):
    pass

#
# Utility functions.
#

def expand_relative(path, basepath):
    """Expand the path `path` relative to the path `basepath`.  If `basepath`
    is not an absolute path it is first expanded relative to Python's current
    CWD to be one."""
    # BELOW FAILS!!!!!
    #path = os.path.expanduser(path)
    #path = os.path.expanduser(path)
    if os.path.isabs(path):
        return path
    if not os.path.isabs(basepath):
        basepath = os.path.abspath(basepath)
    joined_path = os.path.abspath(os.path.join(basepath, path))
    return joined_path

"""The levels used in the utility routines below are levels in the calling
stack (examined using inspect).  The level number includes the level of the
utility function itself.  So level 0 is the attribute of the utility function
itself, level 1 is the attribute of the calling function, level 2 is the
function that called the calling function, etc."""

module_info_cache = {} # Save module path info keyed on module name.

def get_calling_module_info(level=2, module_name=None, module_path=None):
    """A higher-level routine to get information about the of a function back
    some number of levels in the call stack (the calling function).  Returns a
    tuple:

       (calling_module_name,
        calling_module,
        calling_module_path,
        calling_module_dir)
    
    Any relative paths are converted to absolute paths and a check is made to
    make sure that the module actually exists at the path.  Absolute paths are
    cached in a dict keyed on module names so we always get the pathname
    calculated on the first call to this program from a given module.  The
    latter is important in cases where the CWD is changed between the initial
    loading time for a module and the time it (indirectly) calls this routine.
    Such problems are rare, but if they occur you can use these two lines
    near the top of the module (before any imports which might change CWD):

       import pytest_helper
       pytest_helper.get_calling_module_info(level=1)

    The module name and/or path can be supplied via the keyword arguments if
    introspection still fails for some reason (or just to slightly improve
    efficiency)."""

    # TODO: make sure this works when the module is actually a package, run
    # from the package's __init__.py file (or however).  Maybe add more
    # checks, but has to work in both cases.

    if module_name:
        calling_module_name = module_name
        calling_module = sys.modules[calling_module_name]
    else:
        calling_module_name, calling_module = get_calling_module(level)

    if module_path:
        calling_module_path = module_path
    elif calling_module_name in module_info_cache:
        return module_info_cache[calling_module_name]
    else:
        calling_module_path = os.path.abspath(calling_module.__file__)

    calling_module_dir = os.path.dirname(calling_module_path)

    # Do an error check to make sure that the detected module directory exists.
    if not os.path.isdir(calling_module_dir):
        raise PytestHelperException("\n\nThe directory\n   {0}\ndoes of the detected"
                "calling module does not exist.\nDid the Python CWD change without"
                " being changed back?\nYou can try importing pytest_helper near the"
                " top of your file and then immediately calling\n"
                "   pytest_helper.get_calling_module_info(level=1)\nafterward.  If"
                " necessary you can set `module_name` and `module_path`"
                "\nexplicitly from keyword arguments.".format(calling_module_dir))

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
# Test this file when invoked as a script.
#

if __name__ == "__main__":
    script_run("test/test_pytest_helper.py")

