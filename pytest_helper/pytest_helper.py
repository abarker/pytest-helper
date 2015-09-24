# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import
import inspect
import sys
import os
from py.test import raises, fail, fixture, skip
import py.test

"""

Helper functions for using pytest.

Later improvement: allow multiple test files to be run, with optional list of testfiles.

As of now things seem working, BUT need to change some naming and interface
stuff.  The auto-import stuff must run regardless of whether run as a script.
So, consider this:

    Just have a single function, maybe just called run or something, which
    takes a kwarg for whether or not to do the script thing, and a kwarg for
    whether or not to do the auto-import thing.  Script can be default, and
    auto-import not (since should ONLY be used in same file as tests are in).

    Another possibility: have two functions, run and run_in_test, with the
    latter always running the stuff but the former only when a script.
    What about when code is test, though?  Then need to also only run for
    scripts or put inside the __main__== conditional.  Should all
    be keyworded or pull one out and make part of the call itself?  Is
    the separation that clean?

Update the docs, too.

"""

# TODO messes up when, for example, your current dir is test but you
# then open (run?) pratt_parser.py as ../pratt_parser.py

# do_imports not working quite right yet


def run_pytest_when_invoked_as_script(testfile_path=None,
                                      testfile_import_dirs=None,
                                      test_subdir=False, # rename: testfile_import_parent
                                      auto_import_pytest_functions=False,
                                      exit=True):

    """Run pytest on the test file when the calling module is run as a script.
    
    The argument `testfile_path` should be the pathname to the test file to be
    run with pytest.  If the path is relative it must be relative to the
    directory of the script which calls this function.  (Using relative paths
    improves portability.)  If `testfile_path` is `None` then pytest will be
    run on the file of the calling script itself, i.e., the tests are assumed
    to be in the same file as the code to test.
    
    The argument `testfile_import_dirs` should be a pathname or a list of
    pathnames of directories that the test file may need to import from and
    which should be added to `sys.path`.  If any of these paths are relative
    paths they should be relative to the directory of the script which calls
    this function.

    Setting `test_subdir` to `True` is just an easy way to add the parent
    directory of the test file to the Python path (since test subdirectories
    are commonly used).

    If `auto_import_pytest_functions` and `testfile_path` are both set then the
    function will always import some pytest function names into the calling
    module's namespace.  That avoids having to explicitly import things like
    `skip` and `fail`.  It only runs when the function is called from the test
    file itself, and in this it runs even when the file is not invoked as a
    script (though it does not do the rest of the things if not run from a
    script).

    After the tests `sys.exit(0)` will be called unless `exit` is set false."""

    if testfile_import_dirs is None:
        testfile_import_dirs = []
    if isinstance(testfile_import_dirs, str):
        testfile_import_dirs = [testfile_import_dirs]
    if test_subdir:
        testfile_import_dirs.append("..")

    calling_module_name, calling_module = get_calling_module(level=3)

    if testfile_path is None and auto_import_pytest_functions:
        do_auto_import_pytest_functions()

    if calling_module_name != "__main__":
        return

    if testfile_path is None:
        testfile_path = calling_module.__file__ # may fail if CWD changed since start?
    testfile_path = os.path.abspath(os.path.expanduser(testfile_path))
    testfile_dir = os.path.dirname(testfile_path)
    #sys.path.insert(0, testfile_dir) # Add testfile dir to sys.path NEEDED OR DELETE?

    for path in testfile_import_dirs:
        if os.path.isabs(path):
            sys.path.insert(0, testfile_dir)
        else:
            if path[-1] != os.path.sep:
                path += os.path.sep
            joined_path = os.path.join(testfile_dir, path)
            #sys.path.insert(0, testfile_dir + "/../")
            #print("inserted this path", joined_path)
            sys.path.insert(0, joined_path)

    # Call pytest.
    py.test.main(["-v", testfile_path]) # needs pytest 2.0

    if exit: sys.exit(0)

def do_auto_import_pytest_functions():
    # Do the automatic imports into the test calling_module.
    g = get_calling_fun_globals_dict(level=3)
    print("name in g is", g["__name__"])
    g["raises"] = raises
    g["fail"] = fail
    g["fixture"] = fixture
    g["skip"] = skip
    from pytest_helper import (copy_locals_to_globals,
            clear_locals_from_globals, show_globals,
            run_pytest_when_invoked_as_script)
    g["copy_locals_to_globals"] = copy_locals_to_globals
    g["clear_locals_from_globals"] = clear_locals_from_globals
    g["show_globals"] = show_globals

# Run test cases when invoked as a script.
#run_pytest_when_invoked_as_a_script("test_pytest_helper_functions.py")

#if __name__ == "__main__":
#    import py.test
#    py.test.main(["-v", "test_pytest_helper_functions.py"]) # needs pytest 2.0
#    sys.exit(0)

# Remember that using locals() and globals() is preferred for getting the
# variable dicts when within the same frame.

#
# Functions for copying locals to globals.
#

class pytest_helper_data(object):
    last_copied = [] # Could probably be module variable, be careful though.

def copy_locals_to_globals():
    """Copy all local variables in the calling function's local scope to the
    global scope of the module where that function was called.  Note that
    directly modifying locals of a function does not work, only globals can be
    modified.  Raises CopyLocalsToGlobalError on any attempt to overwrite
    existing global data.  Also raises CopyLocalsToGlobalError if any variables
    which were copied by a previous call still exist in the global scope."""
    # If the list isn't empty the user forgot to clear it.
    if pytest_helper_data.last_copied:
        raise CopyLocalsToGlobalError("Failure to call clear_locals_from_globals()"
                                      " for previous fixture.")

    fun_locals = get_calling_fun_locals_dict(2)
    g = get_calling_fun_globals_dict(2)
    for k, v in fun_locals.items():
        if k in g: raise CopyLocalsToGlobalError("Attempt to overwrite existing "
                                                 "module-global variable.")
        # The below line should write to the dotted module name instead, to work
        # when run from a different module.
        #exec("global {0}\n{0}=v".format(k), globals(), locals())
        g[k] = fun_locals[k] # works
        pytest_helper_data.last_copied.append(k)

def clear_locals_from_globals():
    """Clear all the variables that were added by copy_locals_to_globals."""
    g = get_calling_fun_globals_dict(2)
    for k in pytest_helper_data.last_copied:
        del g[k]
    pytest_helper_data.last_copied = []

class CopyLocalsToGlobalError(Exception):
    pass

#
# Utility functions.
#

def view_locals_up_stack():
    """To get an idea of what things look like.  Run from somewhere and see."""
    print("Viewing local variable dict keys up the stack.\n")
    num_levels = 4
    for i in reversed(range(num_levels)):
        calling_fun_frame = inspect.stack()[i][0]
        calling_fun_name = inspect.stack()[i][3]
        calling_fun_locals = calling_fun_frame.f_locals
        indent = "   " * (num_levels - i)
        print("{0}{1} -- stack level {2}".format(indent, calling_fun_name, i))
        print("{0}f_locals keys: {1}\n".format(indent, calling_fun_locals.keys()))

def show_globals(level=2, filt=True):
    """Prints the module globals for the module the calling function was called
    in, filtering files starting with '__'.  Useful for testing."""
    print("Globals:")
    g = get_calling_fun_globals_dict(2)
    for k, v in sorted(g.items()):
        if filt and k.startswith("__"): continue
        print("    {0} = {1}".format(k, v))

def get_calling_fun_locals_dict(level=2):
    """Note that in calling this function you have to increase the level by
    one since it is also on the stack when it does the lookup.
       level 0: This function.
       level 1: The function that called this function.
       level 2: The function that called the calling function."""
    calling_fun_frame = inspect.stack()[level][0]
    calling_fun_locals = calling_fun_frame.f_locals
    return calling_fun_locals

def get_calling_fun_globals_dict(level=2):
    """Note that in calling this function you have to increase the level by
    one since it is also on the stack when it does the lookup.
       level 0: This function.
       level 1: The function that called this function.
       level 2: The function that called the calling function."""
    calling_fun_frame = inspect.stack()[level][0]
    calling_fun_globals = calling_fun_frame.f_globals
    return calling_fun_globals

def get_calling_module(level=2):
    """Run this inside a function.  Get the module where the current function
    is being called from.  Returns a tuple (mod_name, module) with the name of
    the module and the module itself.  See stackoverflow.com/questions/1095543/
       level 1: Module for this function.
       level 2: Module for the function calling this one (what you usually want).
       level 3: Module for the function the one calling this one.
    """
    calling_fun_globals = get_calling_fun_globals_dict(level=3) # TODO put in level when works
    calling_module_name = calling_fun_globals["__name__"]
    calling_module = sys.modules[calling_module_name]
    #print("module vars are", calling_fun_globals)
    return (calling_module_name, calling_module)

#
# Other functions.
#

def get_function_frame(back=0):
    """This method uses sys rather than inspect, but I haven't gotten it to
    go back beyond the first level correctly."""
    x = 5
    f = sys._current_frames().values()[0]
    for i in range(back): f = f.f_back
    # print(f.f_locals["x"]) # works!!!
    # Can at least copy to module scope, enclosing fun harder with pytest....
    return

def caller_name(skip=2):
    """This function is from an answer on StackOverflow at:
       http://stackoverflow.com/questions/2654113
       with only slight edits.
    
       Get a name of a caller in the format module.class.method

       `skip` specifies how many levels of stack to skip while getting caller
       name. skip=1 means "who calls me", skip=2 "who calls my caller" etc.

       An empty string is returned if skipped levels exceed stack height
    """
    stack = inspect.stack()
    start = 0 + skip
    if len(stack) < start + 1:
      return ''
    parentframe = stack[start][0]    

    name = []
    module = inspect.getmodule(parentframe)
    # `modname` can be None when frame is executed directly in console
    # consider using __main__
    if module:
        name.append(module.__name__)
    # detect classname
    if 'self' in parentframe.f_locals:
        # I don't know any way to detect call from the object method
        # there seems to be no way to detect static method call - it will
        #      be just a function call
        name.append(parentframe.f_locals['self'].__class__.__name__)
    codename = parentframe.f_code.co_name
    if codename != '<module>':  # top level usually
        name.append(codename) # function or a method
    del parentframe # Remove definition/reference; could set to None.
    return ".".join(name)


#
# Test this file when invoked as a script.
#

run_pytest_when_invoked_as_script("test/test_pytest_helper.py",
                        test_subdir=True, exit=True)

