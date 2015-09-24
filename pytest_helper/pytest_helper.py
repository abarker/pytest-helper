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

Note that the script is run twice unless this call is put near the top
of the file (may be bad for long-running things).  You could always test
the __name__="__main__" twice, it wouldn't really matter.  So keep
checking it here in main function, but also make clear to users that they
can put the code inside a test like that, too.

Remember that using locals() and globals() is preferred for getting the
variable dicts when within the same frame.
"""

# TODO messes up when, for example, your current dir is test but you
# then open (run?) pratt_parser.py as ../pratt_parser.py


def script_run(testfile_path=None,
                      testfile_import_dirs=None,
                      test_subdir=False, # rename: testfile_import_parent
                      auto_import_pytest_functions=False,
                      module_name=None,
                      exit=True):

    """Run pytest on the test file when the calling module is run as a script.
    
    The argument `testfile_path` should be the pathname to the test file to be
    run with pytest.  If the path is relative it must be relative to the
    directory of the script which calls this function.  (Using relative paths
    improves portability.)  If `testfile_path` is `None` then pytest will be
    run on the file of the calling script itself, i.e., the tests are assumed
    to be in the same file as the code to test.  Using relative paths and
    `None` can fail in cases where Python's CWD is changed before this function
    is called (most programs do not change CWD or return it to its previous
    value).  In those cases you can still use an absolute pathname.
    
    The argument `testfile_import_dirs` should be a pathname or a list of
    pathnames of directories that the test file may need to import from and
    which should be added to `sys.path`.  If any of these paths are relative
    paths they should be relative to the directory of the script which calls
    this function.

    Setting `test_subdir` to `True` is just an easy way to add the parent
    directory of the test file to the Python path (since test subdirectories
    are commonly used).


    The `module_name` argument is a fallback in case the calling function's
    module is not correctly located by introspection.  It is usually not
    required (though it is slightly more efficient).  Use it as:
    `module_name=__name__`.

    After the tests `sys.exit(0)` will be called unless `exit` is set false."""

    if module_name:
        calling_module_name = module_name
    else:
        calling_module_name, calling_module = get_calling_module(level=2)

    if calling_module_name != "__main__":
        return

    #
    # After this point we know this function is being called from a script.
    #

    if module_name:
        calling_module = sys.modules[calling_module_name]

    if testfile_import_dirs is None:
        testfile_import_dirs = []
    if isinstance(testfile_import_dirs, str):
        testfile_import_dirs = [testfile_import_dirs]
    if test_subdir:
        testfile_import_dirs.append("..")

    if testfile_path is None:
        testfile_path = calling_module.__file__
    testfile_path = os.path.abspath(os.path.expanduser(testfile_path))
    testfile_dir = os.path.dirname(testfile_path)
    #sys.path.insert(0, testfile_dir) # Add testfile dir to sys.path NEEDED OR DELETE?

    for path in testfile_import_dirs:
        if os.path.isabs(path):
            sys.path.insert(0, testfile_dir)
        else:
            if path[-1] != os.path.sep:
                path += os.path.sep
            joined_path = os.path.abspath(os.path.join(testfile_dir, path))
            #sys.path.insert(0, testfile_dir + "/../")
            if joined_path not in sys.path:
                sys.path.insert(0, os.path.abspath(joined_path))

    # Call pytest.
    py.test.main(["-v", testfile_path]) # needs pytest 2.0

    if exit: sys.exit(0)

def auto_import(noclobber=True):
    """ This function will import some pytest_helper and pytest attributes
    into the calling module's global namespace.  That avoids having to
    explicitly import things like `locals_to_globals,` `skip` and `fail`.  A
    `PytestHelperException` will be raised if any of those globals already
    exist, unless `noclobber` is set false.  This function runs whenever it is
    called, without checking who is calling it."""

    def insert_in_dict(d, name, value):
        if noclobber and name in d:
            raise PytestHelperException("The pytest_helper function auto_import"
                    "\nattempted an overwrite with noclobber set.  The attribute"
                    " is: " + name)
        d[name] = value

    g = get_calling_fun_globals_dict(level=2)
    insert_in_dict(g, "script_run", script_run)
    insert_in_dict(g, "pytest", py.test)
    insert_in_dict(g, "raises", raises)
    insert_in_dict(g, "fail", fail)
    insert_in_dict(g, "fixture", fixture)
    insert_in_dict(g, "skip", skip)
    insert_in_dict(g, "locals_to_globals", locals_to_globals)
    insert_in_dict(g, "clear_locals_from_globals", clear_locals_from_globals)
    insert_in_dict(g, "show_globals", show_globals)
    insert_in_dict(g, "PytestHelperException", PytestHelperException)
    insert_in_dict(g, "LocalsToGlobalsError", LocalsToGlobalsError)

#
# Functions for copying locals to globals.
#

last_copied_names = [] # Saves the most-recently copied attribute names. 

def locals_to_globals(fun_locals=None, mod_globals=None, auto_clear=True):

    """Copy all local variables in the calling function's local scope to the
    global scope of the module where that function was called.  Raises
    `LocalsToGlobalsError` on any attempt to overwrite existing global data.  If
    `auto_clear` is true (the default) it will automatically clear any
    variables it set on the last run before setting the new ones.  If
    `auto_clear` is false then `clear_locals_from_globals` must be explicitly
    called before calling this function again (or else a `LocalsToGlobalsError`
    will be raised).  The argument `fun_locals` can be used as a fallback to
    pass the `locals()` dict from the function in case the introspection
    technique does not work for some reason.  The `mod_globals` argument can
    similarly be passed the `__name__` attribute of the calling module as a
    fallback."""

    #view_locals_up_stack(4) # debugging
    level = 2

    # If the list isn't empty assume the user forgot to clear it.
    if last_copied_names:
        if auto_clear:
            clear_locals_from_globals()
        else:
            raise LocalsToGlobalsError("Failure to call clear_locals_from_globals()"
                                      " after previous copy (auto_clear is False).")

    if not fun_locals:
        fun_locals = get_calling_fun_locals_dict(level)
    if mod_globals:
        funs_mod_globals = mod_globals
    else:
        funs_mod_globals = get_calling_fun_globals_dict(level)

    for k, v in fun_locals.items():
        if k in funs_mod_globals:
            raise LocalsToGlobalsError("Attempt to overwrite existing "
                                      "module-global variable: " + k)
        # The below line should write to the dotted module name instead, to work
        # when run from a different module.
        #exec("global {0}\n{0}=v".format(k), globals(), locals())
        funs_mod_globals[k] = fun_locals[k] # works
        last_copied_names.append(k)

def clear_locals_from_globals():
    """Clear all the variables that were added by locals_to_globals."""
    level = 2
    g = get_calling_fun_globals_dict(level)
    for k in last_copied_names:
        del g[k]
    last_copied_names = []

class PytestHelperException(Exception):
    pass

class LocalsToGlobalsError(PytestHelperException):
    pass

#
# Utility functions.
#

"""Note that levels below include the level of the utility function itself.  So
level 0 is the attribute of the utility function itself, level 1 is the calling
function's attribute, etc."""

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
       level 3: Module for the function that called the one calling this one.
    """
    # Three lines below work when return does not do the __name__ attribute.
    #calling_fun_globals = get_calling_fun_globals_dict(level=level+1)
    #calling_module_name = calling_fun_globals["__name__"]
    #calling_module = sys.modules[calling_module_name]

    # Two lines below work.
    frame = inspect.stack()[level]
    calling_module = inspect.getmodule(frame[0])

    # Four lines below work, using sys rather than inspect.
    # Someone says this way works with pyinstaller, too, but I haven't tried it.
    # Apparently sys._getframe is available with a performance hit in PyPy,
    # but sys._current_frames is less widely available.
    #f = list(sys._current_frames().values())[0]
    #for i in range(level): f = f.f_back
    #calling_module_name = f.f_globals['__name__']
    #calling_module = sys.modules[calling_module_name]

    return (calling_module.__name__, calling_module)

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

script_run("test/test_pytest_helper.py",
                        test_subdir=True, exit=True)

